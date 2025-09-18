#!/usr/bin/env python3
"""Test script to check if blueprint routes work with Flask test client."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_blueprint_routes():
    """Test blueprint routes using Flask test client."""
    print("=== Testing Blueprint Routes with Flask Test Client ===")
    
    with app.test_client() as client:
        # Test the detect endpoint
        print("\n1. Testing /api/detect endpoint:")
        response = client.post('/api/detect', 
                             data=json.dumps({'text': 'This is a test message'}),
                             content_type='application/json')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test the test endpoint
        print("\n2. Testing /api/test-endpoint:")
        response = client.get('/api/test-endpoint')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test health endpoint
        print("\n3. Testing /api/health endpoint:")
        response = client.get('/api/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test root endpoint
        print("\n4. Testing / endpoint:")
        response = client.get('/')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")

if __name__ == "__main__":
    test_blueprint_routes()