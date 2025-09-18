#!/usr/bin/env python3
"""Fixed version of app.py with proper blueprint registration."""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174'])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Firebase service
try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
    print("Firebase service initialized successfully")
except Exception as e:
    print(f"Warning: Firebase service initialization failed: {e}")
    firebase_service = None

# Import and register blueprints
print("Importing blueprints...")

try:
    from routes.content_detection import content_detection_bp
    print(f"✓ content_detection_bp imported: {content_detection_bp}")
except Exception as e:
    print(f"✗ Error importing content_detection_bp: {e}")
    content_detection_bp = None

try:
    from routes.file_upload import file_upload_bp
    print(f"✓ file_upload_bp imported: {file_upload_bp}")
except Exception as e:
    print(f"✗ Error importing file_upload_bp: {e}")
    file_upload_bp = None

try:
    from routes.auth import auth_bp
    print(f"✓ auth_bp imported: {auth_bp}")
except Exception as e:
    print(f"✗ Error importing auth_bp: {e}")
    auth_bp = None

try:
    from routes.test_blueprint import test_bp
    print(f"✓ test_bp imported: {test_bp}")
except Exception as e:
    print(f"✗ Error importing test_bp: {e}")
    test_bp = None

print("Registering blueprints...")

# Register blueprints with proper error handling
if content_detection_bp:
    app.register_blueprint(content_detection_bp, url_prefix='/api')
    print("✓ content_detection_bp registered")

if file_upload_bp:
    app.register_blueprint(file_upload_bp, url_prefix='/api')
    print("✓ file_upload_bp registered")

if auth_bp:
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✓ auth_bp registered")

if test_bp:
    app.register_blueprint(test_bp, url_prefix='/api')
    print("✓ test_bp registered")

# Basic routes
@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Content Detection API is running',
        'version': '1.0.0'
    })

@app.route('/debug/routes')
def list_routes():
    """Debug endpoint to list all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': rule.rule,
            'endpoint': rule.endpoint,
            'methods': list(rule.methods)
        })
    return jsonify(routes)

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'File too large',
        'message': 'File size exceeds 16MB limit'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# Debug: Print all routes after registration
print("\n=== All Registered Routes ===")
with app.app_context():
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
print("=== End of routes ===\n")

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    print(f"Starting server on port {port} with debug={debug_mode}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)