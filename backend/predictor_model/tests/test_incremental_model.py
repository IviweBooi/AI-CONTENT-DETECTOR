#!/usr/bin/env python3
"""
Test script for incremental training model performance
"""

import os
import json
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_latest_model():
    """Load the latest trained model from checkpoints."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to predictor_model, then into incremental_checkpoints
    checkpoint_dir = os.path.join(os.path.dirname(script_dir), "incremental_checkpoints")
    
    if not os.path.exists(checkpoint_dir):
        logger.error("No checkpoint directory found!")
        return None, None
    
    # Find latest model
    model_dirs = [d for d in os.listdir(checkpoint_dir) 
                 if d.startswith("model_after_chunk_")]
    
    if not model_dirs:
        logger.error("No trained models found!")
        return None, None
    
    # Sort by chunk number and get latest
    model_dirs.sort(key=lambda x: int(x.split("_")[-1]))
    latest_model_path = os.path.join(checkpoint_dir, model_dirs[-1])
    
    logger.info(f"Loading model from: {latest_model_path}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("roberta-base")
    model = AutoModelForSequenceClassification.from_pretrained(latest_model_path)
    
    return tokenizer, model

def test_model_performance(tokenizer, model, test_texts, test_labels, max_length=512):
    """Test model performance on given texts."""
    model.eval()
    predictions = []
    
    logger.info(f"Testing on {len(test_texts)} samples...")
    
    with torch.no_grad():
        for text in test_texts:
            # Tokenize
            inputs = tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt"
            )
            
            # Predict
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=-1).item()
            predictions.append(predicted_class)
    
    # Calculate metrics
    accuracy = accuracy_score(test_labels, predictions)
    report = classification_report(test_labels, predictions, 
                                 target_names=['human', 'ai'], 
                                 output_dict=True)
    
    return accuracy, report, predictions

def load_test_data(data_file="trainingDataset.json", test_size=500):
    """Load a small test set from the training data."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to predictor_model, then to the data file
    data_file_path = os.path.join(os.path.dirname(script_dir), data_file)
    with open(data_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Take last 500 samples as test set (not used in training)
    test_data = data[-test_size:]
    
    texts = [item['text'] for item in test_data]
    labels = [1 if item['label'] == 'ai' else 0 for item in test_data]
    
    return texts, labels

def main():
    logger.info("Testing incremental training model performance...")
    
    # Load latest model
    tokenizer, model = load_latest_model()
    if tokenizer is None or model is None:
        logger.error("Failed to load model!")
        return
    
    # Load test data
    test_texts, test_labels = load_test_data()
    logger.info(f"Loaded {len(test_texts)} test samples")
    
    # Test performance
    accuracy, report, predictions = test_model_performance(
        tokenizer, model, test_texts, test_labels
    )
    
    # Print results
    logger.info("\n" + "="*50)
    logger.info("MODEL PERFORMANCE RESULTS")
    logger.info("="*50)
    logger.info(f"Overall Accuracy: {accuracy:.4f}")
    logger.info(f"Human Detection - Precision: {report['human']['precision']:.4f}")
    logger.info(f"Human Detection - Recall: {report['human']['recall']:.4f}")
    logger.info(f"Human Detection - F1: {report['human']['f1-score']:.4f}")
    logger.info(f"AI Detection - Precision: {report['ai']['precision']:.4f}")
    logger.info(f"AI Detection - Recall: {report['ai']['recall']:.4f}")
    logger.info(f"AI Detection - F1: {report['ai']['f1-score']:.4f}")
    logger.info("="*50)
    
    # Test with sample texts
    logger.info("\nTesting with sample texts:")
    sample_texts = [
        "This is a human-written text about artificial intelligence and its applications in modern society.",
        "The implementation of machine learning algorithms requires careful consideration of data preprocessing techniques.",
        "I love spending time with my family during the weekends, especially when we go hiking in the mountains."
    ]
    
    for i, text in enumerate(sample_texts):
        inputs = tokenizer(text, truncation=True, padding=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
        
        prediction = "AI" if predicted_class == 1 else "Human"
        logger.info(f"Sample {i+1}: {prediction} (confidence: {confidence:.4f})")

if __name__ == "__main__":
    main()