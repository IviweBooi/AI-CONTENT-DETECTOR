from flask import Blueprint, jsonify

# Create a simple test blueprint
test_bp = Blueprint('test_blueprint', __name__)

@test_bp.route('/test-endpoint', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify blueprint registration works."""
    return jsonify({
        'status': 'success',
        'message': 'Test blueprint is working!',
        'endpoint': '/api/test-endpoint'
    })

@test_bp.route('/test-post', methods=['POST'])
def test_post():
    """Test POST endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'POST endpoint working!',
        'method': 'POST'
    })