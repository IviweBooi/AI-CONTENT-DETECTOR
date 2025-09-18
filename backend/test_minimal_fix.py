#!/usr/bin/env python3
"""Minimal test to isolate the blueprint registration issue."""

from flask import Flask, jsonify
from flask_cors import CORS

# Create Flask app with minimal configuration
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174'])

print("=== Testing Minimal Blueprint Registration ===")

# Import and register just the content detection blueprint
try:
    from routes.content_detection import content_detection_bp
    print(f"✓ content_detection_bp imported: {content_detection_bp}")
    
    # Register with /api prefix
    app.register_blueprint(content_detection_bp, url_prefix='/api')
    print("✓ content_detection_bp registered")
    
    # Check routes immediately after registration
    print("\n=== Routes after registration ===")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
    
except Exception as e:
    print(f"✗ Error with content_detection_bp: {e}")

# Add a simple test route
@app.route('/test-simple')
def test_simple():
    return jsonify({'message': 'Simple route works'})

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

if __name__ == "__main__":
    print(f"\n=== Starting Minimal Test Server on Port 5002 ===")
    app.run(debug=True, port=5002, host='0.0.0.0')