import requests
import json

# Test with different text samples
test_texts = [
    "This is a simple test message.",
    "The quick brown fox jumps over the lazy dog. This is a classic pangram used for testing.",
    "In conclusion, the implementation of artificial intelligence in modern society presents both opportunities and challenges that must be carefully considered."
]

for i, text in enumerate(test_texts, 1):
    print(f"\n=== Test {i} ===")
    print(f"Text: {text}")
    
    response = requests.post(
        'http://localhost:5000/api/detect',
        json={'text': text},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"AI Probability: {result['result']['ai_probability']}")
        print(f"Human Probability: {result['result']['human_probability']}")
        print(f"Model Confidence: {result['result']['confidence']}")
        print(f"Classification: {result['result']['classification']}")
    else:
        print(f"Error: {response.text}")