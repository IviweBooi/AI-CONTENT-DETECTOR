from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.file_parsers import FileParserFactory

file_upload_bp = Blueprint('file_upload', __name__)

@file_upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return parsed content"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please select a file to upload'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Check file extension
        allowed_extensions = {'.txt', '.pdf', '.docx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': 'Unsupported file type',
                'message': f'Supported formats: {', '.join(allowed_extensions)}'
            }), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Save file to uploads directory
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        
        # Handle duplicate filenames
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        file.save(file_path)
        
        try:
            # Parse the uploaded file using factory pattern
            parser = FileParserFactory.create_parser(file_path)
            content = parser.parse()
            file_info = parser.get_file_info()
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and parsed successfully',
                'filename': os.path.basename(file_path),
                'content': content,
                'file_info': file_info
            })
            
        except Exception as parse_error:
            # Clean up file if parsing fails
            try:
                os.unlink(file_path)
            except OSError:
                pass
            
            return jsonify({
                'error': 'File parsing error',
                'message': f'Could not parse file: {str(parse_error)}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Upload error',
            'message': f'An error occurred during upload: {str(e)}'
        }), 500

@file_upload_bp.route('/supported-formats', methods=['GET'])
def supported_formats():
    """Get list of supported file formats"""
    return jsonify({
        'supported_formats': [
            {
                'extension': '.txt',
                'description': 'Plain text files',
                'mime_types': ['text/plain']
            },
            {
                'extension': '.pdf',
                'description': 'Portable Document Format',
                'mime_types': ['application/pdf']
            },
            {
                'extension': '.docx',
                'description': 'Microsoft Word Document',
                'mime_types': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            }
        ]
    })