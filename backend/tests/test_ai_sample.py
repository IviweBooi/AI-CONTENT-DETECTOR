import requests
import json

# Test the AI-generated sample text
with open('../ai_sample_text.txt', 'r', encoding='utf-8') as f:
    ai_text = f.read().strip()

print("Testing AI-generated sample text...")
print(f"Text length: {len(ai_text)} characters")
print("\n" + "="*60)
print("Sample text:")
print(ai_text[:200] + "..." if len(ai_text) > 200 else ai_text)
print("\n" + "="*60)

response = requests.post(
    'http://localhost:5000/api/detect',
    json={'text': ai_text},
    headers={'Content-Type': 'application/json'}
)

print(f"\nAPI Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"\n🤖 AI Probability: {result['result']['ai_probability']:.1%}")
    print(f"👤 Human Probability: {result['result']['human_probability']:.1%}")
    print(f"🎯 Model Confidence: {result['result']['confidence']:.1%}")
    print(f"📊 Classification: {result['result']['classification']}")
    print(f"⚠️  Risk Level: {result['result']['risk_level']}")
    
    print("\n📝 Feedback Messages:")
    for msg in result['result'].get('feedback_messages', []):
        print(f"  • {msg}")
        
    print("\n💡 Recommendations:")
    for rec in result['result'].get('recommendations', []):
        print(f"  • {rec}")
else:
    print(f"Error: {response.text}")