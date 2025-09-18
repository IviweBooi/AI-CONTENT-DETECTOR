#!/usr/bin/env python3
"""Debug script to check blueprint route registration."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_blueprint():
    """Debug blueprint registration issues."""
    print("=== Blueprint Debug Script ===")
    
    try:
        print("1. Importing content_detection blueprint...")
        from routes.content_detection import content_detection_bp
        print(f"   ✓ Successfully imported: {content_detection_bp}")
        print(f"   ✓ Blueprint name: {content_detection_bp.name}")
        print(f"   ✓ Deferred functions: {len(content_detection_bp.deferred_functions)}")
        
        print("\n2. Checking deferred functions...")
        for i, func in enumerate(content_detection_bp.deferred_functions):
            print(f"   Function {i+1}: {func}")
            
        print("\n3. Importing test blueprint...")
        from routes.test_blueprint import test_bp
        print(f"   ✓ Successfully imported: {test_bp}")
        print(f"   ✓ Blueprint name: {test_bp.name}")
        print(f"   ✓ Deferred functions: {len(test_bp.deferred_functions)}")
        
        print("\n4. Checking test blueprint deferred functions...")
        for i, func in enumerate(test_bp.deferred_functions):
            print(f"   Function {i+1}: {func}")
            
        print("\n5. Creating minimal Flask app to test registration...")
        from flask import Flask
        app = Flask(__name__)
        
        print("   Registering content_detection_bp...")
        app.register_blueprint(content_detection_bp, url_prefix='/api')
        
        print("   Registering test_bp...")
        app.register_blueprint(test_bp, url_prefix='/api')
        
        print("\n6. Checking registered routes...")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                print(f"   Route: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
                
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_blueprint()