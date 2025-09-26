from flask import Blueprint, request, jsonify, send_file
import os
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.file_parsers import FileParserFactory
from utils.ensemble_detector import EnsembleAIDetector
from utils.enhanced_ai_detector import detect_ai_content_enhanced
from utils.report_exporter import export_manager, create_report_from_analysis
from services.firebase_storage_service import get_storage_service
from middleware.auth_middleware import optional_auth, get_current_user

# Import Firebase service
try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
except Exception as e:
    # Warning: Firebase service not available in content_detection: {e}
    firebase_service = None

content_detection_bp = Blueprint('content_detection', __name__)

# Initialize the ensemble detector with pattern analysis
ensemble_detector = EnsembleAIDetector()

def save_scan_result(text_content, analysis_result, source, filename=None, file_type=None, user_id=None, storage_info=None):
    """Save scan result to Firebase or fallback storage."""
    print(f"🔍 DEBUG: save_scan_result called with user_id={user_id}, source={source}")
    try:
        scan_data = {
            'text_content': text_content[:500] + '...' if len(text_content) > 500 else text_content,  # Truncate for storage
            'text_length': len(text_content),
            'analysis_result': analysis_result,
            'source': source,
            'filename': filename,
            'file_type': file_type,
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'user_id': user_id
        }
        
        # Add storage information if provided
        if storage_info:
            scan_data['storage_info'] = storage_info
        
        print(f"🔍 DEBUG: Firebase service available: {firebase_service is not None}")
        if firebase_service:
            try:
                print(f"🔍 DEBUG: Attempting to save scan result to Firebase...")
                doc_id = firebase_service.save_scan_result(scan_data)
                print(f"🔍 DEBUG: Scan saved successfully with doc_id: {doc_id}")
                return doc_id
            except Exception as e:
                print(f"❌ Error saving scan to Firebase: {e}")
                return None
        else:
            print("❌ Firebase service not available, scan result not saved")
            return None
            
    except Exception as e:
        print(f"❌ Error in save_scan_result: {e}")
        return None

@content_detection_bp.route('/detect', methods=['POST'])
@optional_auth
def detect_content():
    """Detect AI-generated content from text input or uploaded file.
    
    Returns:
        JSON response with analysis results and confidence scores.
    """
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
            
            # Analyze the text with enhanced AI detection (CNN + Neural backup)
            result = detect_ai_content_enhanced(text)
            
            # Get current user for scan tracking
            current_user = get_current_user()
            user_id = current_user['uid'] if current_user else None
            
            # Save scan result to Firebase
            scan_id = save_scan_result(text, result, 'text_input', user_id=user_id)
            
            response_data = {
                'success': True,
                'result': result,
                'source': 'text_input'
            }
            
            if scan_id:
                response_data['scan_id'] = scan_id
            
            return jsonify(response_data)
        
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
            
            # Get storage service and current user
            storage_service = get_storage_service()
            current_user = get_current_user()
            user_id = current_user['uid'] if current_user else None
            
            # Process file temporarily (no permanent storage)
            process_result = storage_service.process_file(
                file, 
                user_id=user_id
            )
            
            if not process_result['success']:
                return jsonify({
                    'error': 'File processing failed',
                    'message': process_result.get('error', 'Unknown processing error')
                }), 500
            
            file_path = process_result['file_path']
            filename = secure_filename(file.filename)
            
            try:
                # Parse the file content using factory pattern
                parser = FileParserFactory.create_parser(file_path)
                text = parser.parse()
                
                if not text.strip():
                    return jsonify({
                        'error': 'Empty file',
                        'message': 'The file appears to be empty or unreadable'
                    }), 400
                
                # Analyze the extracted text with enhanced AI detection (CNN + Neural backup)
                result = detect_ai_content_enhanced(text)
                
                # Save scan result to Firebase (without storage info since we're not storing files)
                scan_id = save_scan_result(text, result, 'file_upload', process_result['original_filename'], file_ext, user_id=user_id, storage_info=None)
                
                response_data = {
                    'success': True,
                    'result': result,
                    'content': text,
                    'source': 'file_upload',
                    'filename': process_result['original_filename'],
                    'file_type': file_ext,
                    'processing_info': {
                        'storage_type': process_result['storage_type'],
                        'file_size': process_result['file_size'],
                        'processing_timestamp': process_result['processing_timestamp'],
                        'note': process_result.get('note', 'File processed temporarily')
                    }
                }
                
                if scan_id:
                    response_data['scan_id'] = scan_id
                
                return jsonify(response_data)
                
            finally:
                # Clean up temporary file after processing
                try:
                    storage_service.cleanup_temp_file(file_path)
                except Exception as e:
                    # Warning: Failed to cleanup temporary file {file_path}: {e}
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

@content_detection_bp.route('/export-report', methods=['POST'])
def export_report():
    """Export analysis report in specified format (PDF, JSON, CSV).
    
    Returns:
        File download with the generated report.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must contain JSON data'
            }), 400
        
        # Required fields
        required_fields = ['analysis_results', 'text_content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'Field "{field}" is required'
                }), 400
        
        # Optional fields with defaults
        analysis_results = data['analysis_results']
        text_content = data['text_content']
        export_format = data.get('format', 'pdf').lower()
        report_title = data.get('title', 'AI Content Detection Report')
        
        # Validate export format
        available_formats = export_manager.get_available_formats()
        if export_format not in available_formats:
            return jsonify({
                'error': 'Unsupported export format',
                'message': f'Supported formats: {", ".join(available_formats)}'
            }), 400
        
        # Create report data
        report_data = create_report_from_analysis(
            analysis_results=analysis_results,
            text_content=text_content,
            title=report_title
        )
        
        # Export report
        exported_data, content_type, file_extension = export_manager.export_report(
            report_data, export_format
        )
        
        # Create filename
        safe_title = "".join(c for c in report_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"{safe_title}_{report_data.timestamp.strftime('%Y%m%d_%H%M%S')}{file_extension}"
        
        # Return file
        return send_file(
            io.BytesIO(exported_data),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
        
    except ValueError as e:
        return jsonify({
            'error': 'Export error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': f'An error occurred while exporting report: {str(e)}'
        }), 500

@content_detection_bp.route('/export-formats', methods=['GET'])
def get_export_formats():
    """Get list of available export formats for reports.
    
    Returns:
        JSON response with supported export formats.
    """
    try:
        formats = export_manager.get_available_formats()
        return jsonify({
            'success': True,
            'formats': formats,
            'default': 'pdf'
        })
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': f'An error occurred while getting export formats: {str(e)}'
        }), 500

@content_detection_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint for content detection service.
    
    Returns:
        JSON response with service status and capabilities.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'content_detection',
        'supported_formats': ['.txt', '.pdf', '.docx'],
        'export_formats': export_manager.get_available_formats()
    })