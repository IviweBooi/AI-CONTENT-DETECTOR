from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174'])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'message': 'AI Content Detection API is running',
        'version': '1.0.0'
    })

@app.route('/test')
def test_route():
    """Simple test route"""
    return jsonify({'message': 'Test route works', 'status': 'success'})

@app.route('/debug/routes')
def list_routes():
    """Debug endpoint to list all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify({'routes': routes})

@app.route('/api/analytics/health', methods=['GET'])
def analytics_health():
    """Analytics service health check endpoint."""
    return jsonify({
        'service': 'analytics',
        'status': 'healthy',
        'storage': 'local',
        'firebase_connected': False
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)