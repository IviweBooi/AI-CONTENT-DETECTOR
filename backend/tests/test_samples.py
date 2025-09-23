import requests
import json

# Test samples
test_samples = {
    "casual_human": """Hey, so I was at the grocery store yesterday and this weird thing happened. I'm standing in the cereal aisle, right? And this old guy comes up to me and asks if I know where the "computer cereals" are. I'm like, what? Turns out he was looking for Apple Jacks! I couldn't stop laughing. His grandson had told him to get "computer cereals" as a joke and the poor guy was so confused. We ended up chatting for like 20 minutes about how technology confuses him. Really sweet actually.""",
    
    "technical_human": """The quarterly budget review revealed several discrepancies in our Q3 expenditures. Specifically, the marketing department exceeded their allocated budget by 15%, primarily due to unexpected costs associated with the product launch campaign. However, this overspend was partially offset by savings in the IT department, where we negotiated better rates with our cloud service provider. Moving forward, I recommend implementing monthly budget check-ins to prevent similar overruns.""",
    
    "personal_human": """I can't believe it's been five years since Dad passed away. Sometimes I still pick up the phone to call him when something good happens. Like last week when I got the promotion - my first instinct was to share it with him. Mom says he would have been so proud. I found his old toolbox in the garage yesterday and just sat there holding his hammer, remembering all those Saturday mornings he taught me how to fix things. Some lessons stick with you forever.""",
    
    "academic_human": """The research methodology employed in this study follows a mixed-methods approach, combining quantitative survey data with qualitative interview responses. Participants were recruited through purposive sampling from three universities in the northeastern United States. Data collection occurred over a six-month period, with follow-up interviews conducted three months after initial surveys. This approach allows for triangulation of findings and provides both breadth and depth to our understanding of student experiences.""",
    
    "ai_generated": """Artificial intelligence represents a transformative paradigm shift in computational methodologies. Through sophisticated algorithmic frameworks and machine learning architectures, AI systems demonstrate remarkable capabilities in pattern recognition and data processing. These technological advancements facilitate enhanced decision-making processes across diverse industry verticals, optimizing operational efficiency and driving innovation-centric solutions."""
}

def test_ai_detector(text, sample_name):
    """Test a text sample with the AI detector API"""
    url = "http://localhost:5001/api/detect"
    headers = {"Content-Type": "application/json"}
    data = {"text": text}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print("Response status: {}".format(response.status_code))
        print("Response text: {}".format(response.text[:200]))
        if response.status_code == 200:
            response_data = response.json()
            result = response_data.get('result', {})
            analysis = result.get('analysis', {})
            print("\n=== {} ===".format(sample_name.upper().replace('_', ' ')))
            ai_prob = result.get('ai_probability', 'N/A')
            model_conf = analysis.get('model_confidence', 'N/A')
            if ai_prob != 'N/A':
                print("AI Probability: {:.4f}".format(ai_prob))
            else:
                print("AI Probability: N/A")
            if model_conf != 'N/A':
                print("Model Confidence: {:.4f}".format(model_conf))
            else:
                print("Model Confidence: N/A")
            print("Prediction Method: {}".format(analysis.get('prediction_method', 'N/A')))
            print("Risk Level: {}".format(result.get('risk_level', 'N/A')))
            print("Text Length: {}".format(analysis.get('text_length', 'N/A')))
            return result
        else:
            print("Error testing {}: {} - {}".format(sample_name, response.status_code, response.text))
            return None
    except Exception as e:
        print("Exception testing {}: {}".format(sample_name, str(e)))
        return None

if __name__ == "__main__":
    print("Testing AI Content Detector with Various Text Samples")
    print("=" * 60)
    
    results = {}
    for sample_name, text in test_samples.items():
        result = test_ai_detector(text, sample_name)
        if result:
            results[sample_name] = result
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF RESULTS")
    print("=" * 60)
    for sample_name, result in results.items():
        ai_prob = result.get('ai_probability', 0)
        confidence = result.get('model_confidence', 0)
        print("{}: {:.1%} AI (Confidence: {:.1%})".format(sample_name.replace('_', ' ').title(), ai_prob, confidence))