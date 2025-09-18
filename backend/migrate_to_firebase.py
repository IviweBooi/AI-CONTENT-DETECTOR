#!/usr/bin/env python3
"""
Migration script to transfer existing analytics data from JSON files to Firebase Firestore.

This script will:
1. Load existing analytics data from analytics_data.json
2. Transfer feedback data to Firestore 'feedback' collection
3. Transfer scan data to Firestore 'scans' collection
4. Transfer accuracy feedback to Firestore 'accuracy_feedback' collection
5. Update analytics summary in Firestore
6. Create a backup of the original JSON file

Usage:
    python migrate_to_firebase.py
"""

import os
import sys
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.firebase_service import get_firebase_service
except ImportError as e:
    print(f"Error importing Firebase service: {e}")
    print("Make sure firebase-admin is installed: pip install firebase-admin")
    sys.exit(1)

def backup_json_file(json_file_path):
    """Create a backup of the original JSON file."""
    if os.path.exists(json_file_path):
        backup_path = f"{json_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(json_file_path, backup_path)
        print(f"✓ Created backup: {backup_path}")
        return backup_path
    return None

def load_json_data(json_file_path):
    """Load analytics data from JSON file."""
    if not os.path.exists(json_file_path):
        print(f"❌ JSON file not found: {json_file_path}")
        return None
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded data from {json_file_path}")
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return None

def migrate_feedback_data(firebase_service, feedback_data):
    """Migrate feedback data to Firestore."""
    if not feedback_data:
        print("ℹ️  No feedback data to migrate")
        return 0
    
    migrated_count = 0
    for feedback in feedback_data:
        try:
            # Ensure timestamp is present
            if 'timestamp' not in feedback:
                feedback['timestamp'] = datetime.now().isoformat()
            
            # Add migration metadata
            feedback['migrated_from_json'] = True
            feedback['migration_timestamp'] = datetime.now().isoformat()
            
            doc_id = firebase_service.add_document('feedback', feedback)
            migrated_count += 1
            print(f"  ✓ Migrated feedback {migrated_count}: {doc_id}")
            
        except Exception as e:
            print(f"  ❌ Error migrating feedback {migrated_count + 1}: {e}")
    
    print(f"✓ Migrated {migrated_count} feedback entries")
    return migrated_count

def migrate_scan_data(firebase_service, scan_data):
    """Migrate scan data to Firestore."""
    if not scan_data:
        print("ℹ️  No scan data to migrate")
        return 0
    
    migrated_count = 0
    for scan in scan_data:
        try:
            # Ensure timestamp is present
            if 'timestamp' not in scan:
                scan['timestamp'] = datetime.now().isoformat()
            
            # Add migration metadata
            scan['migrated_from_json'] = True
            scan['migration_timestamp'] = datetime.now().isoformat()
            
            doc_id = firebase_service.add_document('scans', scan)
            migrated_count += 1
            print(f"  ✓ Migrated scan {migrated_count}: {doc_id}")
            
        except Exception as e:
            print(f"  ❌ Error migrating scan {migrated_count + 1}: {e}")
    
    print(f"✓ Migrated {migrated_count} scan entries")
    return migrated_count

def migrate_accuracy_feedback(firebase_service, accuracy_data):
    """Migrate accuracy feedback data to Firestore."""
    if not accuracy_data:
        print("ℹ️  No accuracy feedback data to migrate")
        return 0
    
    migrated_count = 0
    for accuracy in accuracy_data:
        try:
            # Ensure timestamp is present
            if 'timestamp' not in accuracy:
                accuracy['timestamp'] = datetime.now().isoformat()
            
            # Add migration metadata
            accuracy['migrated_from_json'] = True
            accuracy['migration_timestamp'] = datetime.now().isoformat()
            
            doc_id = firebase_service.add_document('accuracy_feedback', accuracy)
            migrated_count += 1
            print(f"  ✓ Migrated accuracy feedback {migrated_count}: {doc_id}")
            
        except Exception as e:
            print(f"  ❌ Error migrating accuracy feedback {migrated_count + 1}: {e}")
    
    print(f"✓ Migrated {migrated_count} accuracy feedback entries")
    return migrated_count

def update_analytics_summary(firebase_service, total_feedback, total_scans, total_accuracy):
    """Update analytics summary in Firestore."""
    try:
        analytics_summary = {
            'total_feedback': total_feedback,
            'total_scans': total_scans,
            'total_accuracy_feedback': total_accuracy,
            'migrated_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'migration_completed': True
        }
        
        firebase_service.add_document('analytics', analytics_summary, 'summary')
        print(f"✓ Updated analytics summary: {total_feedback} feedback, {total_scans} scans, {total_accuracy} accuracy entries")
        
    except Exception as e:
        print(f"❌ Error updating analytics summary: {e}")

def main():
    """Main migration function."""
    print("🚀 Starting Firebase migration...")
    print("=" * 50)
    
    # Initialize Firebase service
    try:
        firebase_service = get_firebase_service()
        print("✓ Firebase service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase service: {e}")
        print("\nPlease ensure:")
        print("1. Firebase service account JSON file is configured")
        print("2. FIREBASE_SERVICE_ACCOUNT_PATH environment variable is set")
        print("3. Firebase project is properly set up")
        return False
    
    # Define JSON file path
    json_file_path = 'analytics_data.json'
    
    # Create backup
    backup_path = backup_json_file(json_file_path)
    
    # Load existing data
    data = load_json_data(json_file_path)
    if not data:
        print("❌ No data to migrate")
        return False
    
    print(f"\n📊 Data summary:")
    print(f"  - Feedback entries: {len(data.get('feedback', []))}")
    print(f"  - Scan entries: {len(data.get('scans', []))}")
    print(f"  - Accuracy feedback: {len(data.get('accuracy_feedback', []))}")
    print(f"  - Total scans (counter): {data.get('total_scans', 0)}")
    
    # Confirm migration
    response = input("\n🤔 Do you want to proceed with the migration? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Migration cancelled")
        return False
    
    print("\n🔄 Starting migration...")
    
    # Migrate data
    feedback_count = migrate_feedback_data(firebase_service, data.get('feedback', []))
    scan_count = migrate_scan_data(firebase_service, data.get('scans', []))
    accuracy_count = migrate_accuracy_feedback(firebase_service, data.get('accuracy_feedback', []))
    
    # Update analytics summary
    total_scans = max(data.get('total_scans', 0), scan_count)
    update_analytics_summary(firebase_service, feedback_count, total_scans, accuracy_count)
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed successfully!")
    print(f"\n📈 Migration summary:")
    print(f"  - Feedback entries migrated: {feedback_count}")
    print(f"  - Scan entries migrated: {scan_count}")
    print(f"  - Accuracy feedback migrated: {accuracy_count}")
    print(f"  - Backup created: {backup_path}")
    
    print("\n💡 Next steps:")
    print("1. Test the application to ensure Firebase integration works")
    print("2. Verify data in Firebase Console")
    print("3. Consider removing the original JSON file after testing")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during migration: {e}")
        sys.exit(1)