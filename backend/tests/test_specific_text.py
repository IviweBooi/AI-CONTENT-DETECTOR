import requests
import json

# Test with the exact text from the user's input
text = """In modern cities, green spaces such as parks, community gardens, and nature reserves play a crucial role in maintaining both environmental balance and human well-being. As urban areas expand, the demand for housing, roads, and businesses often overshadows the need for natural areas. Yet, these green spaces are more than just decorative; they are essential for healthy living.

Firstly, green spaces improve air quality by filtering pollutants and producing oxygen. This is especially important in dense cities where vehicle emissions and industrial activities are constant sources of pollution. Secondly, they provide habitats for birds, insects, and other small wildlife, which helps preserve biodiversity even in highly developed areas.

From a human perspective, parks and gardens offer opportunities for exercise, relaxation, and social interaction. Studies consistently show that spending time in nature reduces stress, boosts mental health, and encourages physical activity. In many communities, green spaces also serve as gathering spots, strengthening social ties and promoting cultural activities.

In the face of climate change and urban overcrowding, investing in and protecting green spaces is not a luxury but a necessity. They are vital lifelines that make cities more livable, sustainable, and resilient for future generations."""

print("Testing the exact text from user input...")
print(f"Text length: {len(text)} characters")
print("\n" + "="*50)

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
    print(f"Risk Level: {result['result']['risk_level']}")
    print("\nFull Response:")
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.text}")