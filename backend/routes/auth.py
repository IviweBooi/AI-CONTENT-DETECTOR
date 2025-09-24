from flask import Blueprint, request, jsonify, g
from datetime import datetime
from middleware.auth_middleware import require_auth, optional_auth, get_current_user

try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
except Exception as e:
    # Warning: Firebase service not available in auth routes: {e}
    firebase_service = None

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify a Firebase ID token and return user information."""
    try:
        if not firebase_service:
            return jsonify({
                'error': 'Authentication service unavailable',
                'message': 'Firebase authentication is not configured'
            }), 503
        
        data = request.get_json() or {}
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({
                'error': 'Missing token',
                'message': 'idToken is required'
            }), 400
        
        # Verify the token
        decoded_token = firebase_service.verify_id_token(id_token)
        
        if not decoded_token:
            return jsonify({
                'error': 'Invalid token',
                'message': 'The provided token is invalid or expired'
            }), 401
        
        # Get additional user information
        user_info = firebase_service.get_user(decoded_token['uid'])
        
        return jsonify({
            'success': True,
            'user': {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'auth_time': decoded_token.get('auth_time'),
                'firebase_claims': decoded_token
            },
            'user_metadata': user_info.get('metadata') if user_info else None
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Token verification failed',
            'message': str(e)
        }), 401

@auth_bp.route('/user/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Get the current user's profile information."""
    try:
        user = get_current_user()
        
        if not firebase_service:
            return jsonify({
                'user': user,
                'message': 'Limited profile information (Firebase not configured)'
            })
        
        # Get detailed user information from Firebase
        user_info = firebase_service.get_user(user['uid'])
        
        return jsonify({
            'success': True,
            'user': {
                'uid': user['uid'],
                'email': user.get('email'),
                'email_verified': user.get('email_verified', False),
                'name': user.get('name'),
                'picture': user.get('picture'),
                'provider_data': user_info.get('provider_data') if user_info else None,
                'metadata': user_info.get('metadata') if user_info else None,
                'custom_claims': user.get('custom_claims', {})
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user profile',
            'message': str(e)
        }), 500

@auth_bp.route('/user/activity', methods=['GET'])
@require_auth
def get_user_activity():
    """Get the current user's activity (scans and feedback)."""
    try:
        user = get_current_user()
        user_id = user['uid']
        
        if not firebase_service:
            return jsonify({
                'error': 'Service unavailable',
                'message': 'Firebase service is not configured'
            }), 503
        
        # Get user's scan results
        scans = firebase_service.get_scan_results(limit=50, user_id=user_id)
        
        # Get user's feedback
        feedback = firebase_service.get_feedback(limit=50)
        # Filter feedback by user (if user_id is stored in feedback)
        user_feedback = [f for f in feedback if f.get('user_id') == user_id]
        
        return jsonify({
            'success': True,
            'activity': {
                'scans': scans,
                'feedback': user_feedback,
                'total_scans': len(scans),
                'total_feedback': len(user_feedback)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user activity',
            'message': str(e)
        }), 500

@auth_bp.route('/create-custom-token', methods=['POST'])
def create_custom_token():
    """Create a custom token for a user (admin only)."""
    try:
        if not firebase_service:
            return jsonify({
                'error': 'Authentication service unavailable',
                'message': 'Firebase authentication is not configured'
            }), 503
        
        data = request.get_json() or {}
        uid = data.get('uid')
        additional_claims = data.get('claims', {})
        
        if not uid:
            return jsonify({
                'error': 'Missing UID',
                'message': 'uid is required'
            }), 400
        
        # Create custom token
        custom_token = firebase_service.create_custom_token(uid, additional_claims)
        
        return jsonify({
            'success': True,
            'custom_token': custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create custom token',
            'message': str(e)
        }), 500

@auth_bp.route('/auth-status', methods=['GET'])
@optional_auth
def auth_status():
    """Check authentication status."""
    user = get_current_user()
    
    return jsonify({
        'authenticated': user is not None,
        'user': {
            'uid': user['uid'],
            'email': user.get('email'),
            'name': user.get('name')
        } if user else None,
        'firebase_available': firebase_service is not None
    })

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout endpoint (client-side token invalidation)."""
    # Note: Firebase tokens are stateless, so logout is primarily client-side
    # This endpoint can be used for logging purposes or additional cleanup
    
    user = get_current_user()
    
    # Log the logout event (optional)
    if firebase_service:
        try:
            logout_data = {
                'user_id': user['uid'],
                'email': user.get('email'),
                'logout_timestamp': datetime.now().isoformat(),
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.remote_addr
            }
            firebase_service.add_document('user_sessions', logout_data)
        except Exception as e:
            # Error logging logout event: {e}
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully',
        'note': 'Please clear the token on the client side'
    })

@auth_bp.route('/user/disable', methods=['POST'])
@require_auth
def disable_account():
    """Disable the current user's account."""
    try:
        user = get_current_user()
        
        if not firebase_service:
            return jsonify({
                'error': 'Account management not available',
                'message': 'Firebase service not configured'
            }), 503
        
        # Disable the user account
        success = firebase_service.disable_user(user['uid'])
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Account has been disabled successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to disable account',
                'message': 'An error occurred while disabling your account'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Failed to disable account',
            'message': str(e)
        }), 500

@auth_bp.route('/user/delete', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete the current user's account and all associated data."""
    try:
        user = get_current_user()
        
        if not firebase_service:
            return jsonify({
                'error': 'Account management not available',
                'message': 'Firebase service not configured'
            }), 503
        
        # Delete the user account and all associated data
        success = firebase_service.delete_user(user['uid'])
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Account and all associated data have been deleted successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to delete account',
                'message': 'An error occurred while deleting your account'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete account',
            'message': str(e)
        }), 500