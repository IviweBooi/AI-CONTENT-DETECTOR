from .file_parsers import FileParserFactory

def parse_file(file_path, file_extension):
    """
    Parse different file types and extract text content using the factory pattern.
    
    Args:
        file_path (str): Path to the file
        file_extension (str): File extension (.txt, .pdf, .docx)
    
    Returns:
        str: Extracted text content
    
    Raises:
        Exception: If file parsing fails
    """
    try:
        # Use the factory to create the appropriate parser
        parser = FileParserFactory.create_parser(file_path, file_extension)
        return parser.parse()
    except Exception as e:
        raise Exception(f"Error parsing {file_extension} file: {str(e)}")

def get_file_info(file_path):
    """
    Get basic information about a file
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        dict: File information
    """
    try:
        # Use the factory to create a parser and get file info
        parser = FileParserFactory.create_parser(file_path)
        return parser.get_file_info()
    except Exception:
        # Fallback for unsupported file types
        import os
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        file_extension = os.path.splitext(file_path)[1].lower()
        
        return {
            'filename': os.path.basename(file_path),
            'extension': file_extension,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified_time': stat.st_mtime
        }