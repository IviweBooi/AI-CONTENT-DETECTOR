from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174'])

# Initialize Firebase service
try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
    print("Firebase service initialized successfully")
except Exception as e:
    print(f"Warning: Firebase service initialization failed: {e}")
    print("Falling back to local JSON storage")
    firebase_service = None

# Fallback analytics data storage
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
if not firebase_service:
    load_analytics_data()

@app.route('/')
def home():
    return jsonify({'message': 'Analytics server running', 'status': 'healthy'})

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
            'error': str(e)
        }), 500

@app.route('/api/analytics/scan', methods=['POST'])
def analytics_scan():
    """Analytics scan endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create feedback entry
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'feedback_type': data.get('feedback_type', 'scan'),
            'content_type': data.get('content_type'),
            'prediction': data.get('prediction'),
            'confidence': data.get('confidence'),
            'user_feedback': data.get('user_feedback')
        }
        
        try:
            if firebase_service:
                # Store in Firebase
                firebase_service.add_document('feedback', feedback_entry)
                
                # Store accuracy feedback if provided
                if data.get('prediction_accuracy') is not None:
                    accuracy_entry = {
                        'scan_id': data.get('scan_id'),
                        'predicted': data.get('predicted'),
                        'actual': data.get('actual'),
                        'accuracy': data.get('prediction_accuracy'),
                        'timestamp': datetime.now().isoformat()
                    }
                    firebase_service.add_document('accuracy_feedback', accuracy_entry)
                    
            else:
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
                
                # Update scan count
                analytics_data['total_scans'] = analytics_data.get('total_scans', 0) + 1
                save_analytics_data()
                
        except Exception as e:
            print(f"Error storing analytics data: {e}")
            return jsonify({'error': 'Failed to store analytics data'}), 500
        
        return jsonify({
            'message': 'Analytics data stored successfully',
            'status': 'success',
            'storage': 'firebase' if firebase_service else 'local'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/feedback', methods=['POST'])
def analytics_feedback():
    """Analytics feedback endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create feedback entry
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': data.get('type'),
            'comment': data.get('comment', ''),
            'result_id': data.get('resultId'),
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        try:
            if firebase_service:
                # Store in Firebase
                firebase_service.add_document('user_feedback', feedback_entry)
            else:
                # Store locally
                analytics_data['feedback'].append(feedback_entry)
                save_analytics_data()
                
        except Exception as e:
            print(f"Error storing feedback data: {e}")
            return jsonify({'error': 'Failed to store feedback data'}), 500
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'status': 'success',
            'storage': 'firebase' if firebase_service else 'local'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting analytics server on port 5003...")
    app.run(debug=True, host='0.0.0.0', port=5003, use_reloader=False)