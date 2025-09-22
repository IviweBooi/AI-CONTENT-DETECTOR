#!/usr/bin/env python3
"""
Test script for the newly trained AI detection model.
This script loads the trained model and tests it with sample texts.
"""

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainedModelTester:
    def __init__(self, model_path="roberta-base-openai-detector"):
        """Initialize the model tester with the trained model."""
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_model(self):
        """Load the trained model and tokenizer."""
        try:
            logger.info(f"Loading model from {self.model_path}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained("roberta-base")
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def predict(self, text):
        """Predict if text is AI-generated or human-written."""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1)
        
        # Convert to readable format
        ai_probability = probabilities[0][1].item()  # Probability of AI-generated
        human_probability = probabilities[0][0].item()  # Probability of human-written
        predicted_class = "AI-generated" if prediction.item() == 1 else "Human-written"
        
        return {
            "prediction": predicted_class,
            "ai_probability": ai_probability,
            "human_probability": human_probability,
            "confidence": max(ai_probability, human_probability)
        }
    
    def test_samples(self):
        """Test the model with various sample texts."""
        test_samples = [
            {
                "text": "The quick brown fox jumps over the lazy dog. This is a simple sentence that humans often write.",
                "expected": "Human-written",
                "description": "Simple human-like text"
            },
            {
                "text": "In accordance with the aforementioned parameters and considering the multifaceted implications of the proposed methodology, it is imperative to acknowledge that the comprehensive analysis yields substantive insights into the underlying mechanisms.",
                "expected": "AI-generated",
                "description": "Formal AI-like text"
            },
            {
                "text": "I love pizza! It's my favorite food. Yesterday I went to this amazing Italian restaurant with my friends and we had the best time ever.",
                "expected": "Human-written",
                "description": "Casual human conversation"
            },
            {
                "text": "The implementation of advanced machine learning algorithms facilitates the optimization of computational processes through the utilization of sophisticated neural network architectures that demonstrate enhanced performance metrics.",
                "expected": "AI-generated",
                "description": "Technical AI-like text"
            },
            {
                "text": "Hey, what's up? Just wanted to check in and see how you're doing. Hope everything's going well!",
                "expected": "Human-written",
                "description": "Informal human message"
            }
        ]
        
        logger.info("Testing model with sample texts...")
        results = []
        
        for i, sample in enumerate(test_samples, 1):
            logger.info(f"\n--- Test {i}: {sample['description']} ---")
            logger.info(f"Text: {sample['text'][:100]}...")
            logger.info(f"Expected: {sample['expected']}")
            
            try:
                result = self.predict(sample['text'])
                logger.info(f"Predicted: {result['prediction']}")
                logger.info(f"Confidence: {result['confidence']:.3f}")
                logger.info(f"AI Probability: {result['ai_probability']:.3f}")
                logger.info(f"Human Probability: {result['human_probability']:.3f}")
                
                # Check if prediction matches expected
                correct = result['prediction'] == sample['expected']
                logger.info(f"Correct: {'✓' if correct else '✗'}")
                
                results.append({
                    "test_id": i,
                    "description": sample['description'],
                    "expected": sample['expected'],
                    "predicted": result['prediction'],
                    "confidence": result['confidence'],
                    "correct": correct,
                    "ai_probability": result['ai_probability'],
                    "human_probability": result['human_probability']
                })
                
            except Exception as e:
                logger.error(f"Error predicting sample {i}: {e}")
                results.append({
                    "test_id": i,
                    "description": sample['description'],
                    "error": str(e)
                })
        
        return results
    
    def evaluate_performance(self, results):
        """Evaluate overall model performance."""
        valid_results = [r for r in results if 'correct' in r]
        
        if not valid_results:
            logger.error("No valid results to evaluate")
            return
        
        total_tests = len(valid_results)
        correct_predictions = sum(1 for r in valid_results if r['correct'])
        accuracy = correct_predictions / total_tests
        
        avg_confidence = sum(r['confidence'] for r in valid_results) / total_tests
        
        logger.info(f"\n=== MODEL PERFORMANCE SUMMARY ===")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Correct predictions: {correct_predictions}")
        logger.info(f"Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        logger.info(f"Average confidence: {avg_confidence:.3f}")
        
        return {
            "accuracy": accuracy,
            "total_tests": total_tests,
            "correct_predictions": correct_predictions,
            "average_confidence": avg_confidence
        }

def main():
    """Main function to test the trained model."""
    logger.info("Starting model testing...")
    
    # Initialize tester
    tester = TrainedModelTester()
    
    # Load model
    if not tester.load_model():
        logger.error("Failed to load model. Exiting.")
        return
    
    # Test with samples
    results = tester.test_samples()
    
    # Evaluate performance
    performance = tester.evaluate_performance(results)
    
    # Save results
    output_file = "model_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "performance": performance,
            "detailed_results": results
        }, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")
    logger.info("Model testing completed!")

if __name__ == "__main__":
    main()