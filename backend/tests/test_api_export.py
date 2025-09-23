#!/usr/bin/env python3
"""
Test script for the API report export endpoints
"""

import requests
import json
import os

def test_api_export():
    """Test the API export endpoints."""
    base_url = "http://127.0.0.1:5000/api"
    
    print("🧪 Testing API Report Export Endpoints")
    print("=" * 50)
    
    # Test 1: Get available export formats
    print("📋 Testing /export-formats endpoint...")
    try:
        response = requests.get(f"{base_url}/export-formats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Available formats: {data['formats']}")
            print(f"   Default format: {data['default']}")
            available_formats = data['formats']
        else:
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        return
    
    print()
    
    # Sample analysis results for testing
    sample_data = {
        "analysis_results": {
            "ai_probability": 0.85,
            "human_probability": 0.15,
            "confidence": 0.92,
            "classification": "Highly Likely AI-Generated",
            "risk_level": "High",
            "detection_method": "neural",
            "confidence_indicators": [
                "🎯 High confidence in detection results",
                "🤖 Very strong AI indicators detected"
            ],
            "feedback_messages": [
                "Strong AI patterns detected",
                "High confidence in classification"
            ],
            "individual_results": {
                "neural": {"probability": 0.87, "confidence": 0.91}
            }
        },
        "text_content": "This is a sample text that demonstrates the capabilities of artificial intelligence in content generation. The text exhibits patterns commonly associated with AI-generated content, including structured formatting and technical terminology.",
        "title": "API Test Report",
        "format": "pdf"  # Will be changed for each test
    }
    
    # Test 2: Export reports in different formats
    print("📤 Testing /export-report endpoint...")
    
    # Create output directory
    os.makedirs("api_test_exports", exist_ok=True)
    
    for format_name in available_formats:
        print(f"\n   Testing {format_name.upper()} export...")
        
        # Update format in request data
        test_data = sample_data.copy()
        test_data["format"] = format_name
        test_data["title"] = f"API Test Report - {format_name.upper()}"
        
        try:
            response = requests.post(
                f"{base_url}/export-report",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                # Save the exported file
                content_disposition = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    filename = f"api_test_report.{format_name}"
                
                file_path = os.path.join("api_test_exports", filename)
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"      ✅ Success! File saved: {file_path}")
                print(f"      📊 Size: {len(response.content):,} bytes")
                print(f"      📋 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                
            else:
                print(f"      ❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"      Error: {response.text}")
                    
        except Exception as e:
            print(f"      💥 Exception: {str(e)}")
    
    # Test 3: Error handling
    print("\n🔧 Testing error handling...")
    
    # Test missing required fields
    print("   Testing missing required fields...")
    try:
        response = requests.post(
            f"{base_url}/export-report",
            json={"format": "pdf"},  # Missing analysis_results and text_content
            headers={"Content-Type": "application/json"}
        )
        print(f"      Status: {response.status_code}")
        if response.status_code == 400:
            error_data = response.json()
            print(f"      ✅ Correctly rejected: {error_data.get('message')}")
        else:
            print(f"      ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"      💥 Exception: {str(e)}")
    
    # Test invalid format
    print("   Testing invalid export format...")
    try:
        invalid_data = sample_data.copy()
        invalid_data["format"] = "invalid_format"
        
        response = requests.post(
            f"{base_url}/export-report",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"      Status: {response.status_code}")
        if response.status_code == 400:
            error_data = response.json()
            print(f"      ✅ Correctly rejected: {error_data.get('message')}")
        else:
            print(f"      ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"      💥 Exception: {str(e)}")
    
    print("\n🎉 API export testing completed!")
    print(f"📁 Check the 'api_test_exports' directory for generated files.")

if __name__ == "__main__":
    try:
        test_api_export()
    except Exception as e:
        print(f"💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()