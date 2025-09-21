import json

def analyze_dataset():
    with open('trainingDataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_samples = len(data)
    human_samples = sum(1 for x in data if x["label"] == "human")
    ai_samples = sum(1 for x in data if x["label"] == "ai")
    
    text_lengths = [len(x["text"]) for x in data]
    min_length = min(text_lengths)
    max_length = max(text_lengths)
    avg_length = sum(text_lengths) // len(text_lengths)
    
    print(f"Dataset Analysis:")
    print(f"Total samples: {total_samples}")
    print(f"Human samples: {human_samples} ({human_samples/total_samples*100:.1f}%)")
    print(f"AI samples: {ai_samples} ({ai_samples/total_samples*100:.1f}%)")
    print(f"Text lengths - Min: {min_length}, Max: {max_length}, Avg: {avg_length}")
    
    # Check for very short texts
    short_texts = sum(1 for length in text_lengths if length < 50)
    print(f"Texts shorter than 50 chars: {short_texts}")
    
    return total_samples, human_samples, ai_samples

if __name__ == "__main__":
    analyze_dataset()