import requests
import json
import os
import pytest

def test_ai_sample_text():
    """Test the AI-generated sample text detection."""
    # Test the AI-generated sample text
    sample_file = os.path.join(os.path.dirname(__file__), 'ai_sample_text.txt')
    
    if not os.path.exists(sample_file):
        pytest.skip(f"Sample file not found: {sample_file}")
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        ai_text = f.read().strip()

    print("Testing AI-generated sample text...")
    print(f"Text length: {len(ai_text)} characters")
    print("\n" + "="*60)
    print("Sample text:")
    print(ai_text[:200] + "..." if len(ai_text) > 200 else ai_text)
    print("\n" + "="*60)

    # Skip this test if the backend server is not running
    try:
        response = requests.post(
            'http://localhost:5000/api/detect',
            json={'text': ai_text},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
    except requests.exceptions.RequestException:
        pytest.skip("Backend server not running on localhost:5000")

    print(f"\nAPI Response Status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    result = response.json()
    assert 'result' in result, "Response should contain 'result' key"
    
    detection_result = result['result']
    
    # Verify required fields are present
    required_fields = ['ai_probability', 'human_probability', 'confidence', 'classification', 'risk_level']
    for field in required_fields:
        assert field in detection_result, f"Missing required field: {field}"
    
    print(f"\n🤖 AI Probability: {detection_result['ai_probability']:.1%}")
    print(f"👤 Human Probability: {detection_result['human_probability']:.1%}")
    print(f"🎯 Model Confidence: {detection_result['confidence']:.1%}")
    print(f"📊 Classification: {detection_result['classification']}")
    print(f"⚠️  Risk Level: {detection_result['risk_level']}")
    
    # Verify probabilities sum to 1
    total_prob = detection_result['ai_probability'] + detection_result['human_probability']
    assert abs(total_prob - 1.0) < 0.01, f"Probabilities should sum to 1, got {total_prob}"
    
    print("\n📝 Feedback Messages:")
    for msg in detection_result.get('feedback_messages', []):
        print(f"  • {msg}")
        
    print("\n💡 Recommendations:")
    for rec in detection_result.get('recommendations', []):
        print(f"  • {rec}")