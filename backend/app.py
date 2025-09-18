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

# Fallback analytics data storage (for when Firebase is not available)
ANALYTICS_FILE = 'analytics_data.json'
analytics_data = {
    'feedback': [],
    'scans': [],
    'total_scans': 0,
    'accuracy_feedback': []
}

def load_analytics_data():
    """Load analytics data from file (fallback when Firebase is not available)."""
    global analytics_data
    try:
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r') as f:
                analytics_data = json.load(f)
    except Exception as e:
        print(f"Error loading analytics data: {e}")

def save_analytics_data():
    """Save analytics data to file (fallback when Firebase is not available)."""
    try:
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics_data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving analytics data: {e}")

# Load existing data on startup (fallback)
if not firebase_service:
    load_analytics_data()

# Import routes - temporarily commented out to debug
# from routes.content_detection import content_detection_bp
# from routes.file_upload import file_upload_bp
# from routes.auth import auth_bp
# from routes.analytics import analytics_bp  # Using direct implementation instead

# Register blueprints - temporarily commented out to debug
# app.register_blueprint(content_detection_bp, url_prefix='/api')
# app.register_blueprint(file_upload_bp, url_prefix='/api')
# app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(analytics_bp, url_prefix='/api/analytics')  # Using direct implementation instead

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
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify({'routes': routes})

@app.route('/test')
def test_route():
    """Simple test route"""
    return jsonify({'message': 'Test route works', 'status': 'success'})

# Analytics routes - direct implementation
@app.route('/api/analytics/health', methods=['GET'])
def analytics_health():
    """Analytics service health check endpoint."""
    try:
        if firebase_service:
            # Get analytics from Firebase
            analytics_summary = firebase_service.get_analytics_summary()
            return jsonify({
                'service': 'analytics',
                'status': 'healthy',
                'storage': 'firebase',
                'total_feedback': analytics_summary.get('total_feedback', 0),
                'total_scans': analytics_summary.get('total_scans', 0),
                'firebase_connected': True,
                'last_updated': analytics_summary.get('updated_at')
            })
        else:
            # Fallback to local storage
            return jsonify({
                'service': 'analytics',
                'status': 'healthy',
                'storage': 'local_json',
                'total_feedback': len(analytics_data['feedback']),
                'total_scans': analytics_data.get('total_scans', 0),
                'firebase_connected': False
            })
    except Exception as e:
        return jsonify({
            'service': 'analytics',
            'status': 'error',
            'error': str(e),
            'firebase_connected': firebase_service is not None
        }), 500

@app.route('/api/analytics/scan', methods=['POST'])
def analytics_scan():
    """Record analytics data for content scans."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create scan entry
        scan_entry = {
            'id': f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'timestamp': datetime.now().isoformat(),
            'content_type': data.get('contentType', 'unknown'),
            'result': data.get('result', 'unknown'),
            'confidence': data.get('confidence', 0.0),
            'processing_time': data.get('processingTime', 0.0),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        if firebase_service:
            # Save to Firebase
            firebase_service.save_analytics_data('scans', scan_entry)
        else:
            # Save to local storage
            analytics_data['scans'].append(scan_entry)
            analytics_data['total_scans'] = len(analytics_data['scans'])
            save_analytics_data()
        
        return jsonify({
            'success': True,
            'message': 'Scan data recorded successfully',
            'scan_id': scan_entry['id']
        }), 200
        
    except Exception as e:
        print(f"Error in analytics scan endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to record scan data',
            'message': str(e)
        }), 500

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
            'feedback_type': data.get('feedback_type'),
            'rating': data.get('rating'),
            'comment': data.get('comment', ''),
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.now().isoformat(),
            'scan_id': data.get('scan_id'),
            'prediction_accuracy': data.get('prediction_accuracy')
        }
        
        # Store feedback using Firebase or fallback to local storage
        if firebase_service:
            try:
                doc_id = firebase_service.save_feedback(feedback_entry)
                feedback_entry['id'] = doc_id
                
                # Store accuracy feedback separately for analytics
                if data.get('prediction_accuracy') is not None:
                    accuracy_entry = {
                        'scan_id': data.get('scan_id'),
                        'predicted': data.get('predicted'),
                        'actual': data.get('actual'),
                        'accuracy': data.get('prediction_accuracy'),
                        'timestamp': datetime.now().isoformat()
                    }
                    firebase_service.add_document('accuracy_feedback', accuracy_entry)
                    
            except Exception as e:
                print(f"Firebase error, falling back to local storage: {e}")
                # Fallback to local storage
                feedback_entry['id'] = len(analytics_data['feedback']) + 1
                analytics_data['feedback'].append(feedback_entry)
                
                if data.get('prediction_accuracy') is not None:
                    accuracy_entry = {
                        'scan_id': data.get('scan_id'),
                        'predicted': data.get('predicted'),
                        'actual': data.get('actual'),
                        'accuracy': data.get('prediction_accuracy'),
                        'timestamp': datetime.now().isoformat()
                    }
                    analytics_data['accuracy_feedback'].append(accuracy_entry)
                
                save_analytics_data()
        else:
            # Use local storage as fallback
            feedback_entry['id'] = len(analytics_data['feedback']) + 1
            analytics_data['feedback'].append(feedback_entry)
            
            if data.get('prediction_accuracy') is not None:
                accuracy_entry = {
                    'scan_id': data.get('scan_id'),
                    'predicted': data.get('predicted'),
                    'actual': data.get('actual'),
                    'accuracy': data.get('prediction_accuracy'),
                    'timestamp': datetime.now().isoformat()
                }
                analytics_data['accuracy_feedback'].append(accuracy_entry)
            
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