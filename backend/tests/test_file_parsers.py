import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from utils.file_parsers import (
    FileParser, TxtFileParser, PdfFileParser, DocxFileParser, 
    FileParserFactory
)

class TestFileParserFactory:
    """Test cases for FileParserFactory"""
    
    def test_create_txt_parser(self):
        """Test creating TXT parser"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            parser = FileParserFactory.create_parser(tmp_path)
            assert isinstance(parser, TxtFileParser)
        finally:
            os.unlink(tmp_path)
    
    def test_create_pdf_parser(self):
        """Test creating PDF parser"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake pdf content')
            tmp_path = tmp.name
        
        try:
            parser = FileParserFactory.create_parser(tmp_path)
            assert isinstance(parser, PdfFileParser)
        finally:
            os.unlink(tmp_path)
    
    def test_create_docx_parser(self):
        """Test creating DOCX parser"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'PK fake docx content')
            tmp_path = tmp.name
        
        try:
            parser = FileParserFactory.create_parser(tmp_path)
            assert isinstance(parser, DocxFileParser)
        finally:
            os.unlink(tmp_path)
    
    def test_create_parser_with_explicit_extension(self):
        """Test creating parser with explicit extension"""
        with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            parser = FileParserFactory.create_parser(tmp_path, '.txt')
            assert isinstance(parser, TxtFileParser)
        finally:
            os.unlink(tmp_path)
    
    def test_unsupported_extension(self):
        """Test error for unsupported file extension"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                FileParserFactory.create_parser(tmp_path)
            assert 'Unsupported file extension' in str(exc_info.value)
            assert '.xyz' in str(exc_info.value)
        finally:
            os.unlink(tmp_path)
    
    def test_get_supported_extensions(self):
        """Test getting supported extensions"""
        extensions = FileParserFactory.get_supported_extensions()
        assert '.txt' in extensions
        assert '.pdf' in extensions
        assert '.docx' in extensions
        assert '.text' in extensions
    
    def test_is_supported(self):
        """Test checking if extension is supported"""
        assert FileParserFactory.is_supported('.txt') is True
        assert FileParserFactory.is_supported('.PDF') is True  # Case insensitive
        assert FileParserFactory.is_supported('.xyz') is False
    
    def test_register_parser(self):
        """Test registering a new parser"""
        class CustomParser(FileParser):
            def parse(self):
                return 'custom content'
            
            def get_supported_extensions(self):
                return ['.custom']
        
        # Register new parser
        FileParserFactory.register_parser('.custom', CustomParser)
        
        # Test it's registered
        assert FileParserFactory.is_supported('.custom') is True
        
        # Clean up
        if '.custom' in FileParserFactory._parsers:
            del FileParserFactory._parsers['.custom']
    
    def test_register_invalid_parser(self):
        """Test registering invalid parser class"""
        class InvalidParser:
            pass
        
        with pytest.raises(TypeError) as exc_info:
            FileParserFactory.register_parser('.invalid', InvalidParser)
        assert 'must inherit from FileParser' in str(exc_info.value)

class TestTxtFileParser:
    """Test cases for TxtFileParser"""
    
    def test_get_supported_extensions(self):
        """Test getting supported extensions for TXT parser"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test')
            tmp_path = tmp.name
        
        try:
            parser = TxtFileParser(tmp_path)
            extensions = parser.get_supported_extensions()
            assert '.txt' in extensions
            assert '.text' in extensions
        finally:
            os.unlink(tmp_path)
    
    def test_parse_utf8_file(self):
        """Test parsing UTF-8 text file"""
        content = 'Hello, world! This is a test file.'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            parser = TxtFileParser(tmp_path)
            result = parser.parse()
            assert result == content
        finally:
            os.unlink(tmp_path)
    
    @patch('chardet.detect')
    def test_parse_with_encoding_detection(self, mock_detect):
        """Test parsing with encoding detection"""
        mock_detect.return_value = {'encoding': 'latin-1'}
        content = 'Test content'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='latin-1') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            parser = TxtFileParser(tmp_path)
            result = parser.parse()
            assert result == content
            mock_detect.assert_called_once()
        finally:
            os.unlink(tmp_path)
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file"""
        with pytest.raises(FileNotFoundError):
            TxtFileParser('/non/existent/file.txt')
    
    def test_parse_empty_file(self):
        """Test parsing empty file"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            parser = TxtFileParser(tmp_path)
            result = parser.parse()
            assert result == ''
        finally:
            os.unlink(tmp_path)
    
    @patch('builtins.open', side_effect=Exception('Read error'))
    def test_parse_read_error(self, mock_open):
        """Test parsing when file read fails"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            parser = TxtFileParser(tmp_path)
            with pytest.raises(Exception) as exc_info:
                parser.parse()
            assert 'TXT parsing error' in str(exc_info.value)
        finally:
            os.unlink(tmp_path)

class TestPdfFileParser:
    """Test cases for PdfFileParser"""
    
    def test_get_supported_extensions(self):
        """Test getting supported extensions for PDF parser"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake content')
            tmp_path = tmp.name
        
        try:
            parser = PdfFileParser(tmp_path)
            extensions = parser.get_supported_extensions()
            assert '.pdf' in extensions
        finally:
            os.unlink(tmp_path)
    
    @patch('utils.file_parsers.PdfReader')
    def test_parse_success(self, mock_pdf_reader):
        """Test successful PDF parsing"""
        # Mock PDF reader
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = 'Page 1 content'
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = 'Page 2 content'
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake content')
            tmp_path = tmp.name
        
        try:
            parser = PdfFileParser(tmp_path)
            result = parser.parse()
            assert 'Page 1 content' in result
            assert 'Page 2 content' in result
            assert '\n\n' in result  # Pages should be separated
        finally:
            os.unlink(tmp_path)
    
    @patch('utils.file_parsers.PdfReader')
    def test_parse_empty_pdf(self, mock_pdf_reader):
        """Test parsing PDF with no readable text"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ''
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake content')
            tmp_path = tmp.name
        
        try:
            parser = PdfFileParser(tmp_path)
            with pytest.raises(Exception) as exc_info:
                parser.parse()
            assert 'No readable text found in PDF' in str(exc_info.value)
        finally:
            os.unlink(tmp_path)
    
    @patch('utils.file_parsers.PdfReader', side_effect=Exception('PDF error'))
    def test_parse_pdf_error(self, mock_pdf_reader):
        """Test parsing when PDF reading fails"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake content')
            tmp_path = tmp.name
        
        try:
            parser = PdfFileParser(tmp_path)
            with pytest.raises(Exception) as exc_info:
                parser.parse()
            assert 'PDF parsing error' in str(exc_info.value)
        finally:
            os.unlink(tmp_path)

class TestDocxFileParser:
    """Test cases for DocxFileParser"""
    
    def test_get_supported_extensions(self):
        """Test getting supported extensions for DOCX parser"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'PK fake docx content')
            tmp_path = tmp.name
        
        try:
            parser = DocxFileParser(tmp_path)
            extensions = parser.get_supported_extensions()
            assert '.docx' in extensions
        finally:
            os.unlink(tmp_path)
    
    @patch('utils.file_parsers.Document')
    def test_parse_success(self, mock_document):
        """Test successful DOCX parsing"""
        # Mock paragraphs
        mock_para1 = MagicMock()
        mock_para1.text = 'First paragraph'
        mock_para2 = MagicMock()
        mock_para2.text = 'Second paragraph'
        
        # Mock table
        mock_cell1 = MagicMock()
        mock_cell1.text = 'Cell 1'
        mock_cell2 = MagicMock()
        mock_cell2.text = 'Cell 2'
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_doc.tables = [mock_table]
        mock_document.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'PK fake docx content')
            tmp_path = tmp.name
        
        try:
            parser = DocxFileParser(tmp_path)
            result = parser.parse()
            assert 'First paragraph' in result
            assert 'Second paragraph' in result
            assert 'Cell 1 | Cell 2' in result
        finally:
            os.unlink(tmp_path)
    
    @patch('utils.file_parsers.Document')
    def test_parse_empty_docx(self, mock_document):
        """Test parsing DOCX with no readable text"""
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc.tables = []
        mock_document.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'PK fake docx content')
            tmp_path = tmp.name
        
        try:
            parser = DocxFileParser(tmp_path)
            with pytest.raises(Exception) as exc_info:
                parser.parse()
            assert 'No readable text found in DOCX file' in str(exc_info.value)
        finally:
            os.unlink(tmp_path)
    
    @patch('utils.file_parsers.Document', side_effect=Exception('DOCX error'))
    def test_parse_docx_error(self, mock_document):
        """Test parsing when DOCX reading fails"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'PK fake docx content')
            tmp_path = tmp.name
        
        try:
            parser = DocxFileParser(tmp_path)
            with pytest.raises(Exception) as exc_info:
                parser.parse()
            assert 'DOCX parsing error' in str(exc_info.value)
        finally:
            os.unlink(tmp_path)

class TestFileParserBase:
    """Test cases for FileParser base class functionality"""
    
    def test_get_file_info(self):
        """Test getting file information"""
        content = 'Test file content'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            parser = TxtFileParser(tmp_path)
            info = parser.get_file_info()
            
            assert info['filename'] == os.path.basename(tmp_path)
            assert info['extension'] == '.txt'
            assert info['size_bytes'] > 0
            assert info['size_mb'] >= 0
            assert 'modified_time' in info
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_not_exists(self):
        """Test validation for non-existent file"""
        with pytest.raises(FileNotFoundError):
            TxtFileParser('/non/existent/file.txt')
    
    def test_validate_file_is_directory(self):
        """Test validation when path is a directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(ValueError) as exc_info:
                TxtFileParser(tmp_dir)
            assert 'Path is not a file' in str(exc_info.value)