# Troubleshooting Guide

## Firebase-Related Errors

### ERR_BLOCKED_BY_CLIENT Errors

If you're seeing `ERR_BLOCKED_BY_CLIENT` errors in the browser console, this is typically caused by:

#### 1. Ad Blockers
- **uBlock Origin, AdBlock Plus, etc.** may block Firebase requests
- **Solution**: Add `firestore.googleapis.com` and `firebasestorage.googleapis.com` to your ad blocker's whitelist
- **Alternative**: Temporarily disable your ad blocker for `localhost:5173`

#### 2. Browser Extensions
- Privacy-focused extensions may block third-party requests
- **Solution**: Try using an incognito/private browsing window
- **Alternative**: Disable extensions temporarily to test

#### 3. Corporate/Network Firewalls
- Some corporate networks block Firebase services
- **Solution**: Try using a different network or mobile hotspot
- **Contact**: Your IT administrator to whitelist Firebase domains

### CORS Policy Errors

If you're seeing CORS policy errors for Firebase Storage:

#### 1. Authentication Issues
- Make sure you're signed in to the application
- **Solution**: Sign out and sign back in
- **Check**: Your Firebase project authentication settings

#### 2. Firebase Project Configuration
- Verify your Firebase project is properly configured
- **Check**: Firebase Console > Project Settings > General
- **Verify**: Your domain is added to authorized domains

#### 3. Storage Rules
- Firebase Storage rules may be too restrictive
- **Check**: Firebase Console > Storage > Rules
- **Verify**: Rules allow authenticated users to read/write

### Quick Fixes

#### For Development
1. **Clear Browser Cache**: Clear all browser data for localhost
2. **Restart Browser**: Close and reopen your browser
3. **Try Different Browser**: Test with Chrome, Firefox, or Edge
4. **Check Network**: Try a different internet connection

#### For Production
1. **Update Firebase Config**: Ensure all environment variables are correct
2. **Check Domain Settings**: Verify authorized domains in Firebase Console
3. **Review Storage Rules**: Ensure rules allow necessary operations
4. **Monitor Firebase Console**: Check for any service outages

### Fallback Behavior

The application is designed to work even when Firebase services are unavailable:

- **File Upload**: Falls back to direct backend upload
- **Authentication**: Core features work without cloud storage
- **Analysis**: Text analysis works independently of Firebase

### Getting Help

If you continue experiencing issues:

1. **Check Browser Console**: Look for specific error messages
2. **Try Incognito Mode**: Rules out extension conflicts
3. **Test Different Network**: Identifies network-related blocks
4. **Contact Support**: Provide browser console logs and error details

### Environment Variables

Ensure your `.env` file has the correct Firebase configuration:

```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

Get these values from: Firebase Console > Project Settings > General > Your apps > Web app > Config