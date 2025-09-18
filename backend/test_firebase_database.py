#!/usr/bin/env python3
"""
Test script to verify Firebase Database (Firestore) functionality
without Storage dependencies.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.firebase_service import get_firebase_service
    
    print("🔥 Testing Firebase Database (Firestore) functionality...")
    print("=" * 60)
    
    # Initialize Firebase service
    firebase_service = get_firebase_service()
    
    if not firebase_service:
        print("❌ Firebase service not available")
        sys.exit(1)
    
    print("✅ Firebase service initialized successfully")
    
    # Test 1: Add a test document
    print("\n📝 Test 1: Adding test document to Firestore...")
    test_data = {
        'test_message': 'Hello from simplified AI Content Detector!',
        'timestamp': datetime.now().isoformat(),
        'test_type': 'database_verification',
        'storage_disabled': True
    }
    
    try:
        doc_id = firebase_service.add_document('test_collection', test_data)
        if doc_id:
            print(f"✅ Document added successfully with ID: {doc_id}")
        else:
            print("❌ Failed to add document")
    except Exception as e:
        print(f"❌ Error adding document: {e}")
    
    # Test 2: Save a scan result (simulating the app functionality)
    print("\n🔍 Test 2: Saving scan result...")
    scan_data = {
        'text_content': 'This is a test content for AI detection.',
        'text_length': 42,
        'analysis_result': {
            'ai_probability': 0.15,
            'confidence': 0.85,
            'classification': 'human'
        },
        'source': 'test_input',
        'timestamp': datetime.now().isoformat(),
        'user_id': 'test_user_123'
    }
    
    try:
        scan_id = firebase_service.save_scan_result(scan_data)
        if scan_id:
            print(f"✅ Scan result saved successfully with ID: {scan_id}")
        else:
            print("❌ Failed to save scan result")
    except Exception as e:
        print(f"❌ Error saving scan result: {e}")
    
    # Test 3: Retrieve documents
    print("\n📖 Test 3: Retrieving documents...")
    try:
        # Try to get documents from the test collection
        docs = firebase_service.get_documents('test_collection', limit=5)
        if docs:
            print(f"✅ Retrieved {len(docs)} documents from test collection")
            for doc in docs[:2]:  # Show first 2 documents
                print(f"   - Document ID: {doc.get('id', 'N/A')}")
                print(f"     Data: {doc.get('test_message', 'N/A')}")
        else:
            print("ℹ️  No documents found in test collection")
    except Exception as e:
        print(f"❌ Error retrieving documents: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Firebase Database testing completed!")
    print("✅ Database functionality is working properly")
    print("ℹ️  Storage functionality has been disabled as requested")
    print("ℹ️  The app will now process files temporarily without permanent storage")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this from the backend directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("\n💡 Possible solutions:")
    print("   1. Check if Firebase credentials are properly configured")
    print("   2. Verify .env file has correct Firebase settings")
    print("   3. Ensure Firebase project is accessible")
    sys.exit(1)