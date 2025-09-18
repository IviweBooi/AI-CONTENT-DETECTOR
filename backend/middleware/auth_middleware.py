from functools import wraps
from flask import request, jsonify, g
import os

try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
except Exception as e:
    print(f"Warning: Firebase service not available in auth middleware: {e}")
    firebase_service = None

def require_auth(f):
    """Decorator to require Firebase authentication for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firebase_service:
            # If Firebase is not available, skip authentication in development
            if os.getenv('FLASK_ENV') == 'development':
                g.user = {'uid': 'dev-user', 'email': 'dev@example.com'}
                return f(*args, **kwargs)
            else:
                return jsonify({
                    'error': 'Authentication service unavailable',
                    'message': 'Firebase authentication is not configured'
                }), 503
        
        # Get the authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'Missing authorization header',
                'message': 'Please provide an Authorization header with Bearer token'
            }), 401
        
        # Extract the token
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                raise ValueError('Invalid authorization scheme')
        except ValueError:
            return jsonify({
                'error': 'Invalid authorization header',
                'message': 'Authorization header must be in format: Bearer <token>'
            }), 401
        
        # Verify the token
        try:
            decoded_token = firebase_service.verify_id_token(token)
            if not decoded_token:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'The provided token is invalid or expired'
                }), 401
            
            # Store user info in Flask's g object for use in the route
            g.user = decoded_token
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'error': 'Token verification failed',
                'message': f'Failed to verify token: {str(e)}'
            }), 401
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication - sets g.user if token is valid, but doesn't require it."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.user = None  # Default to no user
        
        if not firebase_service:
            return f(*args, **kwargs)
        
        # Get the authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                scheme, token = auth_header.split(' ', 1)
                if scheme.lower() == 'bearer':
                    decoded_token = firebase_service.verify_id_token(token)
                    if decoded_token:
                        g.user = decoded_token
            except Exception:
                # Silently ignore authentication errors for optional auth
                pass
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get the current authenticated user from Flask's g object."""
    return getattr(g, 'user', None)

def is_authenticated():
    """Check if the current request is authenticated."""
    return get_current_user() is not None