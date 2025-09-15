from flask import Blueprint, request, jsonify, send_file
import os
import io
from werkzeug.utils import secure_filename
from utils.file_parsers import FileParserFactory
from utils.enhanced_ai_detector import detect_ai_content_enhanced as detect_ai_content
from utils.report_exporter import export_manager, create_report_from_analysis

content_detection_bp = Blueprint('content_detection', __name__)

@content_detection_bp.route('/detect', methods=['POST'])
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