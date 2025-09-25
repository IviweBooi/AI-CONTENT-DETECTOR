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
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175'])

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

# Import routes
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

# from routes.analytics import analytics_bp  # Using direct implementation instead

# Register blueprints
print("Registering blueprints...")
if content_detection_bp:
    print(f"Content detection blueprint has {len(content_detection_bp.deferred_functions)} deferred functions")
    app.register_blueprint(content_detection_bp, url_prefix='/api')
    print("✓ content_detection_bp registered")
else:
    print("✗ content_detection_bp not registered (import failed)")

if file_upload_bp:
    app.register_blueprint(file_upload_bp, url_prefix='/api')
    print("✓ file_upload_bp registered")

if auth_bp:
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✓ auth_bp registered")

if test_bp:
    print(f"Test blueprint has {len(test_bp.deferred_functions)} deferred functions")
    app.register_blueprint(test_bp, url_prefix='/api')
    print("✓ test_bp registered")

# app.register_blueprint(analytics_bp, url_prefix='/api/analytics')  # Using direct implementation instead

# Debug: Check what routes are actually registered
print("\n=== DEBUG: Routes registered after blueprint registration ===")
for rule in app.url_map.iter_rules():
    print(f"Route: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
print("=== End of route debug ===\n")

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

@app.route('/api/analytics/user-scans/<user_id>', methods=['GET', 'OPTIONS'])
def get_user_scans(user_id):
    """Get scan history for a specific user."""
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        user_scans = []
        
        try:
            if firebase_service:
                # Fetch user scans from Firebase
                print(f"🔍 Fetching scans for user_id: {user_id}")
                user_scans = firebase_service.get_collection(
                    collection='scans',
                    where_filters=[('user_id', '==', user_id)]
                )
                print(f"🔍 Found {len(user_scans)} scans for user {user_id}")
            else:
                # Fetch from local storage - scans are stored in 'feedback' array with feedback_type='scan'
                print(f"🔍 Using local storage, fetching scans for user_id: {user_id}")
                user_scans = [scan for scan in analytics_data['feedback'] 
                             if scan.get('user_id') == user_id and scan.get('feedback_type') == 'scan']
                print(f"🔍 Found {len(user_scans)} scans in local storage")
                
        except Exception as e:
            print(f"❌ Error fetching user scans: {e}")
            return jsonify({'error': 'Failed to fetch scan history'}), 500
        
        # Sort by timestamp (newest first) and limit to last 10 scans
        user_scans.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        user_scans = user_scans[:10]
        
        return jsonify({
            'scans': user_scans,
            'total': len(user_scans),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500





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
    port = int(os.getenv('PORT', 5001))
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)