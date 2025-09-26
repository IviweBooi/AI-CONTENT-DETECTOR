# Analytics Microservice Setup Guide

This guide explains how to set up and run the analytics microservice for the AI Content Detector application.

## Architecture Overview

The analytics functionality has been separated into a dedicated microservice (`analytics_server.py`) that runs independently from the main application. This provides better scalability, maintainability, and fault isolation.

### Services:
- **Main App** (`app.py`): Runs on port 5001 - Content detection and file upload
- **Analytics Server** (`analytics_server.py`): Runs on port 5003 - Analytics data collection and reporting
- **Frontend** (`npm run dev`): Runs on port 5173 - User interface

## Quick Start

### 1. Start the Analytics Server
```bash
cd backend
python analytics_server.py
```
The analytics server will start on `http://localhost:5003`

### 2. Start the Main Application (Optional)
```bash
cd backend
python app_simple.py
```
The main app will start on `http://localhost:5001`

### 3. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:5173`

## Analytics Server Features

### Endpoints
- `GET /api/analytics/health` - Health check and statistics
- `POST /api/analytics/scan` - Record scan analytics data
- `GET /` - Server status

### Data Storage
The analytics server supports two storage modes:

#### Firebase (Recommended)
- Real-time data synchronization
- Scalable cloud storage
- Automatic backups

#### Local JSON Fallback
- Stores data in `analytics_data.json`
- Used when Firebase is unavailable
- Suitable for development/testing

## Firebase Setup (Optional)

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Firestore Database
4. Generate service account key

### 2. Configure Environment
Create a `.env` file in the backend directory:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
```

### 3. Install Dependencies
```bash
pip install firebase-admin python-dotenv
```

## Testing the Analytics Server

### Health Check
```bash
curl http://localhost:5003/api/analytics/health
```

### Submit Analytics Data
```bash
curl -X POST http://localhost:5003/api/analytics/scan \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Sample content",
    "result": "human",
    "confidence": 0.85,
    "content_type": "text"
  }'
```

## Frontend Integration

The frontend automatically connects to the analytics server on port 5003. The configuration is in `frontend/src/services/api.js`:

```javascript
// Analytics API URL - separate analytics server
const ANALYTICS_API_URL = import.meta.env.VITE_ANALYTICS_API_URL || 'http://localhost:5003/api';
```

### Environment Variables
You can override the analytics server URL by setting:
```env
VITE_ANALYTICS_API_URL=http://your-analytics-server:5003/api
```

## Troubleshooting

### Analytics Server Won't Start
1. Check if port 5003 is available
2. Verify Python dependencies are installed
3. Check Firebase configuration if using Firebase

### Frontend Can't Connect to Analytics
1. Ensure analytics server is running on port 5003
2. Check CORS configuration in `analytics_server.py`
3. Verify the analytics API URL in frontend configuration

### Firebase Connection Issues
1. Verify `.env` file configuration
2. Check Firebase project permissions
3. Ensure service account has Firestore access

## Production Deployment

### Docker Setup (Recommended)
Create a `Dockerfile` for the analytics server:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5003
CMD ["python", "analytics_server.py"]
```

### Environment Configuration
- Use environment variables for all configuration
- Enable Firebase for production data storage
- Configure proper CORS origins
- Use a production WSGI server (e.g., Gunicorn)

## Monitoring

The analytics server provides health check endpoints for monitoring:
- Server status: `GET /`
- Detailed health: `GET /api/analytics/health`

Monitor these endpoints to ensure the service is running properly.