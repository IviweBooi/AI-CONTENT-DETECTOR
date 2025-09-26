#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Epoch 5 AI Detection Model
This script tests the model on known AI and human text samples to provide concrete accuracy metrics.
"""

import os
import sys
import argparse
import torch
import torch.nn.functional as F
import numpy as np
from datetime import datetime
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'character-based-cnn-master'))

from src.model import CharacterLevelCNN
from src import utils

class ModelTester:
    def __init__(self, model_path, alphabet, number_of_characters, extra_characters=""):
        self.model_path = model_path
        self.alphabet = alphabet
        self.number_of_characters = number_of_characters
        self.extra_characters = extra_characters
        self.use_cuda = torch.cuda.is_available()
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the trained model"""
        print(f"Loading model: {self.model_path}")
        
        # Create args object similar to predict_epoch5.py
        class Args:
            def __init__(self, alphabet, number_of_characters, extra_characters):
                self.alphabet = alphabet
                self.number_of_characters = number_of_characters
                self.extra_characters = extra_characters
                self.max_length = 1500
                self.number_of_classes = 2
                self.dropout_input = 0.1
                self.steps = ["lower"]
        
        args = Args(self.alphabet, self.number_of_characters, self.extra_characters)
        
        # Initialize model
        self.model = CharacterLevelCNN(args, args.number_of_classes)
        
        # Load state dict
        state = torch.load(self.model_path, map_location='cpu' if not self.use_cuda else 'cuda')
        self.model.load_state_dict(state)
        self.model.eval()
        
        if self.use_cuda:
            self.model = self.model.to("cuda")
        
    def predict_text(self, text):
        """Predict if text is human or AI generated"""
        # Create args object for preprocessing
        class Args:
            def __init__(self, text, alphabet, number_of_characters, extra_characters):
                self.text = text
                self.alphabet = alphabet
                self.number_of_characters = number_of_characters
                self.extra_characters = extra_characters
                self.max_length = 1500
                self.steps = ["lower"]
        
        args = Args(text, self.alphabet, self.number_of_characters, self.extra_characters)
        
        # Preprocess input
        processed_input = utils.preprocess_input(args)
        processed_input = torch.tensor(processed_input)
        processed_input = processed_input.unsqueeze(0)
        
        if self.use_cuda:
            processed_input = processed_input.to("cuda")
        
        # Make prediction
        with torch.no_grad():
            prediction = self.model(processed_input)
            probabilities = F.softmax(prediction, dim=1)
            probabilities = probabilities.detach().cpu().numpy()[0]
            
        return probabilities  # [human_prob, ai_prob]

def get_test_samples():
    """Return known AI and human text samples for testing"""
    
    # Known HUMAN-written text samples (from various sources)
    human_samples = [
        # Personal narrative
        "I can't believe I'm finally graduating! It feels like just yesterday I was a freshman, completely lost and overwhelmed. Now here I am, about to walk across that stage. My parents are so proud, and honestly, I'm pretty proud of myself too. College wasn't easy - there were nights I wanted to give up, especially during organic chemistry. But I stuck with it, and now I'm heading to medical school in the fall!",
        
        # Social media style
        "OMG you guys!! Just had the WORST day ever 😭 First my coffee machine broke, then I missed my bus, and THEN it started raining right when I forgot my umbrella. But you know what? My bestie surprised me with pizza and we binge-watched Netflix all evening. Sometimes the worst days turn into the best nights ❤️ #blessed #friendship",
        
        # Blog post style
        "Traveling solo for the first time was terrifying and exhilarating. I remember standing in the airport, clutching my boarding pass, wondering if I was making a huge mistake. But three weeks later, as I sat watching the sunset over the Mediterranean, I knew it was the best decision I'd ever made. I learned more about myself in those three weeks than I had in years.",
        
        # Review style
        "This restaurant is absolutely incredible! I've been coming here for years, and they never disappoint. The pasta is always perfectly al dente, and don't even get me started on their tiramisu - it's like a little piece of heaven. The staff knows me by name now, which makes me feel like family. Definitely my go-to spot for special occasions.",
        
        # Casual conversation
        "So my neighbor's dog keeps getting into my yard and digging up my flowers. I've talked to them about it twice, but nothing's changed. I don't want to be that person who calls animal control, but I'm running out of patience. Any suggestions? I really don't want this to turn into a big neighborhood drama.",
        
        # Personal reflection
        "Turning 30 hit me harder than I expected. I thought I'd have everything figured out by now - career, relationships, maybe even kids. Instead, I'm still figuring out what I want to be when I grow up. But maybe that's okay? Maybe life isn't about having all the answers, but about being brave enough to keep asking questions.",
        
        # Storytelling
        "My grandmother used to tell the most amazing stories about growing up during the war. She'd describe how they'd hide in the basement during air raids, and how she met my grandfather at a dance when she was just seventeen. Her eyes would light up when she talked about their first date - a picnic by the river where he brought sandwiches and she brought homemade cookies.",
        
        # Opinion piece
        "I know everyone's obsessed with productivity hacks and optimization, but honestly? Sometimes I think we've forgotten how to just... be. Like, when's the last time you sat somewhere without your phone and just watched people? Or listened to music without doing anything else? We're so busy trying to maximize every moment that we're missing the actual moments.",
        
        # Technical but personal
        "Been coding for about 5 years now, and I still get that rush when my code finally works after hours of debugging. Today I spent 3 hours chasing down a bug that turned out to be a missing semicolon. Classic! But that moment when everything clicks and the program runs perfectly? That's why I love this job, even when it drives me crazy.",
        
        # Creative writing
        "The old bookstore smelled like vanilla and forgotten dreams. I loved wandering through the narrow aisles, running my fingers along the spines of books that had been loved by strangers. Each one had a story beyond its pages - coffee stains, dog-eared corners, handwritten notes in the margins. This place was where stories came to rest between readers."
    ]
    
    # Known AI-generated text samples (from various AI models)
    ai_samples = [
        # GPT-style academic
        "Artificial intelligence represents a paradigm shift in computational capabilities, offering unprecedented opportunities for automation and optimization across diverse sectors. Machine learning algorithms demonstrate remarkable proficiency in pattern recognition, enabling applications ranging from medical diagnosis to financial forecasting. The integration of neural networks with big data analytics facilitates sophisticated decision-making processes that surpass traditional computational approaches.",
        
        # AI business writing
        "Organizations seeking to enhance operational efficiency must consider implementing comprehensive digital transformation strategies. These initiatives typically involve leveraging cloud-based solutions, optimizing workflow processes, and integrating advanced analytics platforms. Successful implementation requires stakeholder alignment, robust change management protocols, and continuous performance monitoring to ensure sustainable competitive advantages.",
        
        # AI technical documentation
        "The system architecture employs a microservices approach, utilizing containerized applications deployed across distributed infrastructure. Key components include API gateways for request routing, message queues for asynchronous processing, and database clusters for high-availability data storage. This design ensures scalability, fault tolerance, and maintainability while supporting real-time performance requirements.",
        
        # AI marketing copy
        "Discover innovative solutions designed to revolutionize your business operations. Our cutting-edge platform combines advanced analytics with intuitive user interfaces, delivering actionable insights that drive measurable results. Experience seamless integration, enhanced productivity, and unprecedented growth opportunities through our comprehensive suite of enterprise-grade tools and services.",
        
        # AI educational content
        "Climate change mitigation strategies encompass various approaches including renewable energy adoption, carbon sequestration technologies, and sustainable transportation systems. Effective implementation requires coordinated efforts between governmental policies, private sector investments, and individual behavioral modifications. Research indicates that comprehensive approaches yield optimal outcomes for long-term environmental sustainability.",
        
        # AI news style
        "Recent developments in quantum computing technology demonstrate significant progress toward practical applications in cryptography and optimization problems. Leading technology companies have announced breakthrough achievements in quantum supremacy, with implications for cybersecurity, financial modeling, and scientific research. Industry experts anticipate widespread commercial adoption within the next decade.",
        
        # AI research abstract
        "This study examines the correlation between social media engagement patterns and consumer purchasing behaviors across demographic segments. Utilizing machine learning algorithms to analyze large-scale datasets, researchers identified significant predictive relationships between online interactions and transaction frequencies. Findings suggest that targeted marketing strategies can achieve improved conversion rates through personalized content delivery mechanisms.",
        
        # AI policy writing
        "Regulatory frameworks for emerging technologies must balance innovation incentives with consumer protection requirements. Policymakers should consider adaptive governance models that accommodate rapid technological evolution while maintaining appropriate oversight mechanisms. Stakeholder consultation processes ensure comprehensive understanding of implementation challenges and potential unintended consequences across affected industries.",
        
        # AI product description
        "This advanced analytics platform provides comprehensive data visualization capabilities, enabling organizations to transform complex datasets into actionable business intelligence. Features include real-time dashboard creation, automated report generation, and predictive modeling tools. The solution integrates seamlessly with existing enterprise systems, supporting various data formats and providing scalable performance optimization.",
        
        # AI scientific writing
        "Experimental results demonstrate statistically significant improvements in processing efficiency when implementing the proposed algorithmic optimization techniques. Performance metrics indicate enhanced throughput rates and reduced computational overhead compared to baseline methodologies. These findings contribute to the broader understanding of system optimization principles and their practical applications in distributed computing environments."
    ]
    
    return human_samples, ai_samples

def run_comprehensive_test():
    """Run comprehensive testing on the model"""
    
    # Model configuration (matching epoch 5 training)
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+-=<>()[]{}"
    number_of_characters = 69
    extra_characters = ""  # Empty for epoch 5 model
    model_path = "models/model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth"
    
    # Initialize tester
    tester = ModelTester(model_path, alphabet, number_of_characters, extra_characters)
    
    # Get test samples
    human_samples, ai_samples = get_test_samples()
    
    print("=" * 80)
    print("COMPREHENSIVE AI DETECTION MODEL TEST")
    print("=" * 80)
    print(f"Model: {model_path}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Device: {'CUDA' if tester.use_cuda else 'CPU'}")
    print(f"Alphabet Size: {len(alphabet)}")
    print("=" * 80)
    
    # Test results storage
    results = {
        'human_tests': [],
        'ai_tests': [],
        'summary': {}
    }
    
    # Test human samples
    print("\n🧑 TESTING HUMAN-WRITTEN SAMPLES:")
    print("-" * 50)
    human_correct = 0
    
    for i, text in enumerate(human_samples, 1):
        probs = tester.predict_text(text)
        human_prob, ai_prob = probs[0], probs[1]
        predicted_class = "Human" if human_prob > ai_prob else "AI"
        is_correct = predicted_class == "Human"
        
        if is_correct:
            human_correct += 1
            
        result = {
            'sample_id': i,
            'text_preview': text[:100] + "..." if len(text) > 100 else text,
            'human_prob': float(human_prob),
            'ai_prob': float(ai_prob),
            'predicted_class': predicted_class,
            'confidence': float(max(human_prob, ai_prob)),
            'correct': is_correct
        }
        results['human_tests'].append(result)
        
        status = "✅ CORRECT" if is_correct else "❌ WRONG"
        print(f"Sample {i:2d}: {predicted_class} ({max(human_prob, ai_prob):.3f}) {status}")
    
    # Test AI samples
    print("\n🤖 TESTING AI-GENERATED SAMPLES:")
    print("-" * 50)
    ai_correct = 0
    
    for i, text in enumerate(ai_samples, 1):
        probs = tester.predict_text(text)
        human_prob, ai_prob = probs[0], probs[1]
        predicted_class = "Human" if human_prob > ai_prob else "AI"
        is_correct = predicted_class == "AI"
        
        if is_correct:
            ai_correct += 1
            
        result = {
            'sample_id': i,
            'text_preview': text[:100] + "..." if len(text) > 100 else text,
            'human_prob': float(human_prob),
            'ai_prob': float(ai_prob),
            'predicted_class': predicted_class,
            'confidence': float(max(human_prob, ai_prob)),
            'correct': is_correct
        }
        results['ai_tests'].append(result)
        
        status = "✅ CORRECT" if is_correct else "❌ WRONG"
        print(f"Sample {i:2d}: {predicted_class} ({max(human_prob, ai_prob):.3f}) {status}")
    
    # Calculate metrics
    total_samples = len(human_samples) + len(ai_samples)
    total_correct = human_correct + ai_correct
    overall_accuracy = total_correct / total_samples
    human_accuracy = human_correct / len(human_samples)
    ai_accuracy = ai_correct / len(ai_samples)
    
    # Calculate average confidence
    all_confidences = [r['confidence'] for r in results['human_tests'] + results['ai_tests']]
    avg_confidence = np.mean(all_confidences)
    
    # Store summary
    results['summary'] = {
        'total_samples': total_samples,
        'total_correct': total_correct,
        'overall_accuracy': overall_accuracy,
        'human_samples': len(human_samples),
        'human_correct': human_correct,
        'human_accuracy': human_accuracy,
        'ai_samples': len(ai_samples),
        'ai_correct': ai_correct,
        'ai_accuracy': ai_accuracy,
        'average_confidence': avg_confidence,
        'test_date': datetime.now().isoformat()
    }
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Overall Accuracy:     {overall_accuracy:.1%} ({total_correct}/{total_samples})")
    print(f"Human Detection:      {human_accuracy:.1%} ({human_correct}/{len(human_samples)})")
    print(f"AI Detection:         {ai_accuracy:.1%} ({ai_correct}/{len(ai_samples)})")
    print(f"Average Confidence:   {avg_confidence:.1%}")
    print("=" * 80)
    
    # Save results to JSON
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: test_results.json")
    
    return results

if __name__ == "__main__":
    run_comprehensive_test()