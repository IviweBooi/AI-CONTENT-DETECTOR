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

# Analytics data storage
ANALYTICS_FILE = 'analytics_data.json'
analytics_data = {
    'feedback': [],
    'scans': [],
    'total_scans': 0,
    'accuracy_feedback': []
}

def load_analytics_data():
    """Load analytics data from file."""
    global analytics_data
    try:
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r') as f:
                analytics_data = json.load(f)
    except Exception as e:
        print(f"Error loading analytics data: {e}")

def save_analytics_data():
    """Save analytics data to file."""
    try:
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics_data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving analytics data: {e}")

# Load existing data on startup
load_analytics_data()

# Import routes
from routes.content_detection import content_detection_bp
from routes.file_upload import file_upload_bp

# Register blueprints
app.register_blueprint(content_detection_bp, url_prefix='/api')
app.register_blueprint(file_upload_bp, url_prefix='/api')

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Content Detection API is running',
        'version': '1.0.0'
    })

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for AI detection results."""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get('feedback_type'):
            return jsonify({
                'error': 'Missing required field: feedback_type'
            }), 400
        
        # Create feedback entry
        feedback_entry = {
            'id': len(analytics_data['feedback']) + 1,
            'feedback_type': data.get('feedback_type'),
            'rating': data.get('rating'),
            'comment': data.get('comment', ''),
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.now().isoformat(),
            'scan_id': data.get('scan_id'),
            'prediction_accuracy': data.get('prediction_accuracy')
        }
        
        # Store feedback
        analytics_data['feedback'].append(feedback_entry)
        
        # Store accuracy feedback separately for analytics
        if data.get('prediction_accuracy') is not None:
            accuracy_entry = {
                'scan_id': data.get('scan_id'),
                'predicted': data.get('predicted'),
                'actual': data.get('actual'),
                'accuracy': data.get('prediction_accuracy'),
                'timestamp': datetime.now().isoformat()
            }
            analytics_data['accuracy_feedback'].append(accuracy_entry)
        
        # Save to file
        save_analytics_data()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_entry['id'],
            'status': 'success'
        }), 201
        
    except Exception as e:
        print(f"Error in feedback endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/health', methods=['GET'])
def analytics_health():
    """Analytics service health check endpoint."""
    return jsonify({
        'service': 'analytics',
        'status': 'healthy',
        'total_feedback': len(analytics_data['feedback']),
        'total_scans': analytics_data.get('total_scans', 0),
        'data_file': ANALYTICS_FILE,
        'file_exists': os.path.exists(ANALYTICS_FILE)
    })

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

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)