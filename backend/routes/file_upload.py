from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.file_parsers import FileParserFactory
from services.firebase_storage_service import get_storage_service
from middleware.auth_middleware import optional_auth, get_current_user

file_upload_bp = Blueprint('file_upload', __name__)

@file_upload_bp.route('/upload', methods=['POST'])
@optional_auth
def upload_file():
    """Handle file upload and return parsed content.
    
    Supports .txt, .pdf, and .docx files.
    
    Returns:
        JSON response with parsed file content and metadata.
    """
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
        
        # Get storage service and current user
        storage_service = get_storage_service()
        current_user = get_current_user()
        user_id = current_user['uid'] if current_user else None
        
        # Upload file using Firebase Storage service
        upload_result = storage_service.upload_file(
            file, 
            folder='document_uploads',
            user_id=user_id
        )
        
        if not upload_result['success']:
            return jsonify({
                'error': 'Upload failed',
                'message': upload_result.get('error', 'Unknown upload error')
            }), 500
        
        file_path = upload_result['file_path']
        
        try:
            # Parse the uploaded file using factory pattern
            parser = FileParserFactory.create_parser(file_path)
            content = parser.parse()
            file_info = parser.get_file_info()
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and parsed successfully',
                'filename': upload_result['original_filename'],
                'content': content,
                'file_info': file_info,
                'upload_info': {
                    'storage_type': upload_result['storage_type'],
                    'file_path': upload_result['file_path'],
                    'download_url': upload_result.get('download_url'),
                    'file_size': upload_result['file_size'],
                    'upload_timestamp': upload_result['upload_timestamp']
                }
            })
            
        except Exception as parse_error:
            # Clean up file if parsing fails
            try:
                storage_service.delete_file(file_path, upload_result['storage_type'])
            except Exception:
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
    """Get list of supported file formats for upload.
    
    Returns:
        JSON response with supported file extensions and descriptions.
    """
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