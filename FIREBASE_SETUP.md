# Firebase Integration Setup Guide

This guide will help you set up Firebase integration for the AI Content Detector application, including Firestore database, Firebase Authentication, and Firebase Storage.

## Prerequisites

- A Google Cloud Platform account
- A Firebase project
- Python 3.8+ installed
- Node.js 16+ installed (for frontend)

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "ai-content-detector")
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Firebase Services

### Enable Firestore Database

1. In your Firebase project console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for development) or "Start in production mode"
4. Select a location for your database
5. Click "Done"

### Enable Firebase Authentication

1. Go to "Authentication" in the Firebase console
2. Click "Get started"
3. Go to the "Sign-in method" tab
4. Enable the authentication providers you want to use:
   - Email/Password
   - Google
   - GitHub
   - Anonymous (for testing)

### Enable Firebase Storage

1. Go to "Storage" in the Firebase console
2. Click "Get started"
3. Choose "Start in test mode" (for development)
4. Select a location for your storage bucket
5. Click "Done"

## Step 3: Generate Service Account Credentials

1. In the Firebase console, go to "Project settings" (gear icon)
2. Go to the "Service accounts" tab
3. Click "Generate new private key"
4. Download the JSON file
5. Save it securely in your project directory (e.g., `backend/firebase-service-account.json`)

**Important**: Never commit this file to version control!

## Step 4: Configure Environment Variables

### Backend Configuration

1. Copy the example environment file:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Firebase configuration:
   ```env
   # Firebase Configuration
   FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/
   ```

   Replace `your-project-id` with your actual Firebase project ID.

### Frontend Configuration

1. Copy the frontend example environment file:
   ```bash
   cd frontend
   cp .env.example .env
   ```

2. Get your Firebase web app configuration:
   - In Firebase console, go to "Project settings"
   - Scroll down to "Your apps" section
   - Click "Add app" and select "Web"
   - Register your app and copy the config object

3. Add the Firebase config to your frontend `.env` file:
   ```env
   VITE_FIREBASE_API_KEY=your-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   VITE_FIREBASE_APP_ID=your-app-id
   ```

## Step 5: Install Dependencies

### Backend Dependencies

```bash
cd backend
pip install firebase-admin
```

### Frontend Dependencies

```bash
cd frontend
npm install firebase
```

## Step 6: Set Up Firestore Security Rules

1. In the Firebase console, go to "Firestore Database"
2. Go to the "Rules" tab
3. Replace the default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to read/write their own data
    match /scan_results/{document} {
      allow read, write: if request.auth != null;
      allow read: if resource.data.user_id == request.auth.uid;
    }
    
    match /feedback/{document} {
      allow read, write: if request.auth != null;
    }
    
    match /analytics/{document} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
    
    // Allow anonymous users to create scan results (for non-authenticated usage)
    match /scan_results/{document} {
      allow create: if true;
    }
  }
}
```

## Step 7: Set Up Firebase Storage Security Rules

1. In the Firebase console, go to "Storage"
2. Go to the "Rules" tab
3. Replace the default rules with:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Allow authenticated users to upload files
    match /document_uploads/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /scan_uploads/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Allow anonymous uploads to a specific folder (optional)
    match /anonymous_uploads/{allPaths=**} {
      allow write: if true;
      allow read: if request.auth != null;
    }
  }
}
```

## Step 8: Migrate Existing Data (Optional)

If you have existing analytics data in JSON files, you can migrate it to Firestore:

```bash
cd backend
python migrate_to_firebase.py
```

This script will:
- Create a backup of your existing JSON data
- Upload the data to Firestore
- Preserve your existing analytics

## Step 9: Test the Integration

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Test the following features:
   - Content detection (should save to Firestore)
   - File uploads (should use Firebase Storage)
   - User authentication (if implemented in frontend)
   - Analytics dashboard

## Troubleshooting

### Common Issues

1. **"Default credentials not found" error**:
   - Ensure the `FIREBASE_SERVICE_ACCOUNT_PATH` points to the correct JSON file
   - Check that the service account file exists and is readable

2. **Permission denied errors**:
   - Check your Firestore and Storage security rules
   - Ensure the user is properly authenticated

3. **Firebase initialization failed**:
   - Verify all environment variables are set correctly
   - Check that your Firebase project ID is correct

4. **Storage upload failures**:
   - Ensure Firebase Storage is enabled
   - Check storage security rules
   - Verify the storage bucket name is correct

### Development vs Production

- **Development**: Use test mode for Firestore and Storage rules
- **Production**: Implement proper security rules and authentication
- **Environment Variables**: Use different Firebase projects for dev/staging/production

## Security Best Practices

1. **Never commit service account keys** to version control
2. **Use environment variables** for all sensitive configuration
3. **Implement proper Firestore security rules** for production
4. **Enable Firebase App Check** for additional security
5. **Regularly rotate service account keys**
6. **Use Firebase Authentication** for user management
7. **Implement proper CORS settings** for web applications

## API Endpoints with Firebase

The following endpoints now support Firebase integration:

- `POST /api/detect` - Content detection with Firestore logging
- `POST /api/upload` - File upload with Firebase Storage
- `POST /api/feedback` - Feedback storage in Firestore
- `GET /api/analytics` - Analytics from Firestore
- `POST /api/auth/verify-token` - Firebase Authentication
- `GET /api/auth/user/profile` - User profile management
- `GET /api/auth/user/activity` - User activity tracking

## Monitoring and Analytics

Firebase provides built-in monitoring and analytics:

1. **Firestore Usage**: Monitor read/write operations
2. **Storage Usage**: Track file uploads and downloads
3. **Authentication**: Monitor user sign-ins and activity
4. **Performance**: Use Firebase Performance Monitoring

For more detailed information, refer to the [Firebase Documentation](https://firebase.google.com/docs).