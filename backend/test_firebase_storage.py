#!/usr/bin/env python3
"""
Test script to check Firebase Storage configuration
"""
import os
import sys

def test_firebase_storage():
    try:
        from services.firebase_service import get_firebase_service
        firebase_service = get_firebase_service()
        print('✓ Firebase service initialized')
        
        if firebase_service.bucket:
            bucket_name = firebase_service.bucket.name
            print(f'✓ Storage bucket: {bucket_name}')
            
            # Test if we can access the bucket
            try:
                # Try to list some blobs (this will fail if storage is not properly configured)
                blobs = list(firebase_service.bucket.list_blobs(max_results=1))
                print('✓ Storage bucket is accessible')
                print(f'✓ Found {len(blobs)} files in bucket')
                
                # Test if we can get bucket metadata
                bucket_info = firebase_service.bucket.get_blob('test')  # This won't error even if blob doesn't exist
                print('✓ Bucket metadata accessible')
                
            except Exception as e:
                print(f'✗ Storage bucket access error: {e}')
                print('This might indicate:')
                print('  - Storage bucket does not exist in Firebase project')
                print('  - Service account lacks Storage permissions')
                print('  - Storage bucket name is incorrect')
                return False
        else:
            print('✗ Storage bucket not initialized')
            print('Check FIREBASE_STORAGE_BUCKET environment variable')
            return False
            
        return True
        
    except Exception as e:
        print(f'✗ Firebase initialization error: {e}')
        print('This might indicate:')
        print('  - Firebase service account file is missing or invalid')
        print('  - Environment variables are not set correctly')
        print('  - Firebase project is not properly configured')
        return False

if __name__ == '__main__':
    print('Testing Firebase Storage configuration...')
    success = test_firebase_storage()
    if success:
        print('\n✓ Firebase Storage is properly configured!')
    else:
        print('\n✗ Firebase Storage configuration has issues.')
        print('\nTo fix this:')
        print('1. Ensure Firebase Storage is enabled in your Firebase project')
        print('2. Check that FIREBASE_STORAGE_BUCKET environment variable is set')
        print('3. Verify service account has Storage Admin permissions')
        print('4. Make sure the storage bucket exists in your Firebase project')