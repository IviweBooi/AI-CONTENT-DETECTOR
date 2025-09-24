from flask import Blueprint, request, jsonify
from datetime import datetime
import os

# Import services
try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
except Exception as e:
    # Warning: Firebase service not available in analytics: {e}
    firebase_service = None

analytics_bp = Blueprint('analytics', __name__)

# Analytics data storage (fallback when Firebase is not available)
ANALYTICS_FILE = 'analytics_data.json'
analytics_data = {
    'scans': [],
    'feedback': [],
    'accuracy_feedback': [],
    'total_scans': 0
}

def load_analytics_data():
    """Load analytics data from JSON file."""
    global analytics_data
    try:
        if os.path.exists(ANALYTICS_FILE):
            import json
            with open(ANALYTICS_FILE, 'r') as f:
                analytics_data = json.load(f)
    except Exception as e:
        # Error loading analytics data: {e}

def save_analytics_data():
    """Save analytics data to JSON file."""
    try:
        import json
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics_data, f, indent=2)
    except Exception as e:
        print(f"Error saving analytics data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to save analytics data'
        }), 500

# Load analytics data on startup
load_analytics_data()

@analytics_bp.route('/scan', methods=['POST'])
def track_scan():
    """Track scan analytics endpoint."""
    try:
        data = request.get_json() or {}
        
        # Create scan entry
        scan_entry = {
            'content_type': data.get('contentType', 'unknown'),
            'content_length': data.get('contentLength', 0),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        
        # Store scan data using Firebase or fallback to local storage
        if firebase_service:
            try:
                doc_id = firebase_service.add_document('scans', scan_entry)
                scan_entry['id'] = doc_id
                
                # Update analytics summary
                analytics_summary = firebase_service.get_analytics_summary()
                analytics_summary['total_scans'] = analytics_summary.get('total_scans', 0) + 1
                analytics_summary['updated_at'] = datetime.now().isoformat()
                firebase_service.add_document('analytics', analytics_summary, 'summary')
                
            except Exception as e:
                # Firebase error, falling back to local storage: {e}
                # Fallback to local storage
                scan_entry['id'] = len(analytics_data['scans']) + 1
                analytics_data['scans'].append(scan_entry)
                analytics_data['total_scans'] = analytics_data.get('total_scans', 0) + 1
                save_analytics_data()
        else:
            # Use local storage as fallback
            scan_entry['id'] = len(analytics_data['scans']) + 1
            analytics_data['scans'].append(scan_entry)
            analytics_data['total_scans'] = analytics_data.get('total_scans', 0) + 1
            save_analytics_data()
        
        return jsonify({
            'success': True,
            'message': 'Scan tracked successfully',
            'scan_id': scan_entry['id']
        }), 200
        
    except Exception as e:
        # Error in scan tracking endpoint: {e}
        return jsonify({
            'success': False,
            'error': 'Failed to track scan',
            'message': str(e)
        }), 500

@analytics_bp.route('/feedback', methods=['POST'])
def submit_analytics_feedback():
    """Submit feedback for analytics endpoint."""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get('type'):
            return jsonify({
                'success': False,
                'error': 'Missing required field: type'
            }), 400
        
        # Create feedback entry
        feedback_entry = {
            'type': data.get('type'),
            'comment': data.get('comment', ''),
            'result_id': data.get('resultId'),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        
        # Store feedback using Firebase or fallback to local storage
        if firebase_service:
            try:
                doc_id = firebase_service.save_feedback(feedback_entry)
                feedback_entry['id'] = doc_id
                
                # Update analytics summary
                analytics_summary = firebase_service.get_analytics_summary()
                analytics_summary['total_feedback'] = analytics_summary.get('total_feedback', 0) + 1
                analytics_summary['updated_at'] = datetime.now().isoformat()
                firebase_service.add_document('analytics', analytics_summary, 'summary')
                
            except Exception as e:
                # Firebase error, falling back to local storage: {e}
                # Fallback to local storage
                feedback_entry['id'] = len(analytics_data['feedback']) + 1
                analytics_data['feedback'].append(feedback_entry)
                save_analytics_data()
        else:
            # Use local storage as fallback
            feedback_entry['id'] = len(analytics_data['feedback']) + 1
            analytics_data['feedback'].append(feedback_entry)
            save_analytics_data()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_entry['id']
        }), 200
        
    except Exception as e:
        # Error in analytics feedback endpoint: {e}
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback',
            'message': str(e)
        }), 500

@analytics_bp.route('/health', methods=['GET'])
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
                'data_file': ANALYTICS_FILE,
                'file_exists': os.path.exists(ANALYTICS_FILE),
                'firebase_connected': False
            })
    except Exception as e:
        return jsonify({
            'service': 'analytics',
            'status': 'error',
            'error': str(e),
            'firebase_connected': firebase_service is not None
        }), 500