# AI Content Detection Backend

A Flask-based REST API for detecting AI-generated content in text and documents.

## Features

- **File Upload Support**: Accepts TXT, PDF, and DOCX files
- **Text Analysis**: Direct text input analysis
- **AI Detection**: Heuristic-based AI content detection
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Enabled**: Cross-origin requests supported

## API Endpoints

### Health Check
- `GET /` - API health check
- `GET /api/health` - Content detection service health

### Content Detection
- `POST /api/detect` - Analyze text or file for AI content
  - Body (JSON): `{"text": "your text here"}`
  - Body (Form): `file` field with uploaded document

### File Operations
- `POST /api/upload` - Upload and parse file
- `GET /api/supported-formats` - Get supported file formats

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1  # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Development Server**:
   ```bash
   python app.py
   ```

4. **Access API**:
   - Local: http://127.0.0.1:5000
   - Health Check: http://127.0.0.1:5000/

## Environment Variables

Configure in `.env` file:
- `FLASK_DEBUG`: Enable debug mode
- `PORT`: Server port (default: 5000)
- `CORS_ORIGINS`: Allowed frontend origins
- `MAX_CONTENT_LENGTH`: Max file upload size

## File Support

- **TXT**: Plain text files with encoding detection
- **PDF**: Portable Document Format
- **DOCX**: Microsoft Word documents

## AI Detection

Current implementation uses heuristic analysis including:
- Lexical diversity
- Sentence structure patterns
- Repetition analysis
- Formality scoring
- AI-typical phrase detection

*Note: For production use, replace with trained ML models for better accuracy.*

## Development

- **Routes**: `/routes/` - API endpoint definitions
- **Utils**: `/utils/` - File parsing and AI detection logic
- **Uploads**: `/uploads/` - Temporary file storage