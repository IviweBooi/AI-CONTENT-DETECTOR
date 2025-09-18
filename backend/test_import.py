#!/usr/bin/env python3

print("Testing imports...")

try:
    print("Importing content_detection_bp...")
    from routes.content_detection import content_detection_bp
    print(f"✓ content_detection_bp imported successfully: {content_detection_bp}")
    print(f"✓ Blueprint name: {content_detection_bp.name}")
    print(f"✓ Blueprint routes: {list(content_detection_bp.deferred_functions)}")
except Exception as e:
    print(f"✗ Error importing content_detection_bp: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nImporting file_upload_bp...")
    from routes.file_upload import file_upload_bp
    print(f"✓ file_upload_bp imported successfully: {file_upload_bp}")
except Exception as e:
    print(f"✗ Error importing file_upload_bp: {e}")

try:
    print("\nImporting auth_bp...")
    from routes.auth import auth_bp
    print(f"✓ auth_bp imported successfully: {auth_bp}")
except Exception as e:
    print(f"✗ Error importing auth_bp: {e}")

print("\nImport test completed.")