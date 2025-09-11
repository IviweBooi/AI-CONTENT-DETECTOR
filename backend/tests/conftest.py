import pytest
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from flask import Flask
    from flask_cors import CORS
    
    # Create test app
    test_app = Flask(__name__)
    CORS(test_app)
    
    # Test configuration
    test_app.config.update({
        'TESTING': True,
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    })
    
    # Register blueprints
    from routes.content_detection import content_detection_bp
    from routes.file_upload import file_upload_bp
    
    test_app.register_blueprint(content_detection_bp, url_prefix='/api')
    test_app.register_blueprint(file_upload_bp, url_prefix='/api')
    
    with test_app.app_context():
        yield test_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_ai_detector():
    """Mock the AI detector to avoid loading actual models during tests."""
    with patch('utils.ai_detector.AIDetector') as mock:
        mock_instance = MagicMock()
        mock_instance.detect_ai_content.return_value = {
            'is_ai_generated': False,
            'confidence': 0.3,
            'analysis': {
                'perplexity_score': 45.2,
                'burstiness_score': 0.7,
                'linguistic_patterns': ['human-like variation', 'natural flow']
            }
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "This is a sample text for testing purposes. It contains multiple sentences to test the AI detection functionality."

@pytest.fixture
def sample_files():
    """Sample file data for testing file uploads."""
    return {
        'txt_content': b'This is a test text file content.',
        'pdf_content': b'%PDF-1.4 fake pdf content for testing',
        'docx_content': b'PK fake docx content for testing'
    }