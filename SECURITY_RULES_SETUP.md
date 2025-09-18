# Firebase Security Rules Setup Guide

This guide will help you deploy the Firestore and Storage security rules for the AI Content Detector application.

## Overview

We have created two security rules files:
- `firestore.rules` - Controls access to Firestore database
- `storage.rules` - Controls access to Firebase Storage

## Security Rules Features

### Firestore Rules (`firestore.rules`)
- **User-based access control**: Users can only access their own data
- **Email verification requirement**: Enhanced security for verified users
- **Collection-specific rules**:
  - `/users/{userId}` - User profiles (read/write own data)
  - `/detections/{detectionId}` - AI detection results (read/write own results)
  - `/feedback/{feedbackId}` - User feedback (create own, read own)
  - `/analytics/{analyticsId}` - Analytics data (read-only for users)
  - `/files/{fileId}` - File metadata (read/write own files)
  - `/settings/{settingId}` - System settings (read-only)

### Storage Rules (`storage.rules`)
- **File size limits**: 5MB for profile pictures, 10MB for documents
- **File type validation**: Only allowed file types can be uploaded
- **Path-based access control**:
  - `/users/{userId}/profile/` - Profile pictures (own access)
  - `/uploads/{userId}/` - Document uploads (own access)
  - `/temp/{userId}/` - Temporary processing files (own access)
  - `/exports/{userId}/` - Export downloads (own access)
  - `/public/` - Public assets (read-only for all)
  - `/system/` - System files (admin only)

## Deployment Methods

### Method 1: Firebase Console (Recommended for beginners)

#### Deploy Firestore Rules
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to **Firestore Database** → **Rules**
4. Copy the contents of `firestore.rules` file
5. Paste into the rules editor
6. Click **Publish**

#### Deploy Storage Rules
1. In the same Firebase Console project
2. Navigate to **Storage** → **Rules**
3. Copy the contents of `storage.rules` file
4. Paste into the rules editor
5. Click **Publish**

### Method 2: Firebase CLI (Recommended for production)

#### Prerequisites
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project (if not already done)
firebase init
```

#### Deploy Rules
```bash
# Deploy Firestore rules
firebase deploy --only firestore:rules

# Deploy Storage rules
firebase deploy --only storage

# Deploy both at once
firebase deploy --only firestore:rules,storage
```

## Testing Security Rules

### Firestore Rules Testing
1. In Firebase Console → **Firestore Database** → **Rules**
2. Click **Rules playground**
3. Test scenarios:
   - **Authenticated user accessing own data**: Should allow
   - **Authenticated user accessing other user's data**: Should deny
   - **Unauthenticated user accessing any data**: Should deny

### Storage Rules Testing
1. In Firebase Console → **Storage** → **Rules**
2. Click **Rules playground**
3. Test scenarios:
   - **Upload valid file type with correct size**: Should allow
   - **Upload oversized file**: Should deny
   - **Upload invalid file type**: Should deny
   - **Access other user's files**: Should deny

## Security Best Practices Implemented

### 🔒 **Authentication Required**
- All operations require user authentication
- Email verification adds extra security layer

### 👤 **User Isolation**
- Users can only access their own data
- No cross-user data access allowed

### 📁 **File Type Validation**
- Only specific file types allowed for uploads
- Prevents malicious file uploads

### 📏 **Size Limits**
- Profile pictures: 5MB maximum
- Document uploads: 10MB maximum
- Prevents storage abuse

### 🛡️ **Principle of Least Privilege**
- Users get minimal necessary permissions
- System data protected from user access

### 🔍 **Data Validation**
- Required fields enforced on creation
- Data structure validation

## Troubleshooting

### Common Issues

#### "Permission denied" errors
- Check if user is authenticated
- Verify user is accessing their own data
- Ensure required fields are present

#### Rules deployment fails
- Check syntax in rules files
- Ensure Firebase CLI is logged in
- Verify project permissions

#### File upload fails
- Check file size limits
- Verify file type is allowed
- Ensure user is authenticated

### Testing Commands
```bash
# Test rules locally (requires Firebase emulator)
firebase emulators:start --only firestore,storage

# Validate rules syntax
firebase firestore:rules:validate
```

## Next Steps

After deploying security rules:
1. ✅ Test rules with your application
2. ✅ Update frontend to handle authentication
3. ✅ Implement file upload functionality
4. ✅ Test end-to-end workflows
5. ✅ Monitor security rule usage in Firebase Console

## Security Monitoring

- Monitor rule evaluations in Firebase Console
- Set up alerts for unusual access patterns
- Regularly review and update rules as needed
- Keep rules version controlled in your repository

---

**Important**: These rules provide a secure foundation but should be reviewed and adjusted based on your specific application requirements and security policies.