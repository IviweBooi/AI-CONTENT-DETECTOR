#!/usr/bin/env python3
"""Test script that exactly mimics app.py setup to debug blueprint registration."""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
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
    print("Falling back to local JSON storage")
    firebase_service = None

print("=== Testing Blueprint Registration (Exact App.py Setup) ===")

# Import routes exactly like app.py
print("Importing blueprints...")
try:
    from routes.content_detection import content_detection_bp
    print(f"✓ content_detection_bp imported: {content_detection_bp}")
except Exception as e:
    print(f"✗ Error importing content_detection_bp: {e}")
    content_detection_bp = None

try:
    from routes.test_blueprint import test_bp
    print(f"✓ test_bp imported: {test_bp}")
except Exception as e:
    print(f"✗ Error importing test_bp: {e}")
    test_bp = None

# Register blueprints exactly like app.py
print("Registering blueprints...")
if content_detection_bp:
    print(f"Content detection blueprint has {len(content_detection_bp.deferred_functions)} deferred functions")
    app.register_blueprint(content_detection_bp, url_prefix='/api')
    print("✓ content_detection_bp registered")
else:
    print("✗ content_detection_bp not registered (import failed)")

if test_bp:
    print(f"Test blueprint has {len(test_bp.deferred_functions)} deferred functions")
    app.register_blueprint(test_bp, url_prefix='/api')
    print("✓ test_bp registered")

# Add the same routes as app.py
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

print("\n=== Checking Registered Routes ===")
with app.app_context():
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

print(f"\n=== Starting Test Server on Port 5001 ===")
if __name__ == "__main__":
    app.run(debug=True, port=5001)