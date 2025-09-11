from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.file_parsers import FileParserFactory
from utils.ai_detector import detect_ai_content

content_detection_bp = Blueprint('content_detection', __name__)

@content_detection_bp.route('/detect', methods=['POST'])
def detect_content():
    """Detect AI-generated content from text or file"""
    try:
        # Check if request contains text or file
        if 'text' in request.json if request.is_json else False:
            # Direct text analysis
            text = request.json.get('text', '').strip()
            if not text:
                return jsonify({
                    'error': 'Empty text',
                    'message': 'Please provide text to analyze'
                }), 400
            
            # Analyze the text
            result = detect_ai_content(text)
            return jsonify({
                'success': True,
                'result': result,
                'source': 'text_input'
            })
        
        elif 'file' in request.files:
            # File upload analysis
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({
                    'error': 'No file selected',
                    'message': 'Please select a file to analyze'
                }), 400
            
            # Check file extension
            allowed_extensions = {'.txt', '.pdf', '.docx'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                return jsonify({
                    'error': 'Unsupported file type',
                    'message': f'Supported formats: {', '.join(allowed_extensions)}'
                }), 400
            
            # Save uploaded file to uploads directory
            filename = secure_filename(file.filename)
            upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            try:
                # Parse the file content using factory pattern
                parser = FileParserFactory.create_parser(file_path)
                text = parser.parse()
                
                if not text.strip():
                    return jsonify({
                        'error': 'Empty file',
                        'message': 'The file appears to be empty or unreadable'
                    }), 400
                
                # Analyze the extracted text
                result = detect_ai_content(text)
                
                print(f"DEBUG: Extracted text length: {len(text)}")
                print(f"DEBUG: Text preview: {text[:100]}...")
                print(f"DEBUG: About to return response with content field")
                
                return jsonify({
                    'success': True,
                    'result': result,
                    'content': text,
                    'source': 'file_upload',
                    'filename': file.filename,
                    'file_type': file_ext
                })
                
            finally:
                # Clean up uploaded file
                try:
                    os.unlink(file_path)
                except OSError:
                    pass
        
        else:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide either text or a file to analyze'
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': f'An error occurred while processing: {str(e)}'
        }), 500

@content_detection_bp.route('/health', methods=['GET'])
def health():
    """Health check for content detection service"""
    return jsonify({
        'status': 'healthy',
        'service': 'content_detection',
        'supported_formats': ['.txt', '.pdf', '.docx']
    })