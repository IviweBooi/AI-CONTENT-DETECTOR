#!/usr/bin/env python3
"""
Script to run the trained CNN model from epoch 5
"""

import torch
import torch.nn.functional as F
import argparse
import sys
import os

# Add the character-based-cnn-master directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'character-based-cnn-master'))

from src.model import CharacterLevelCNN
from src import utils

def load_epoch5_model():
    """Load the epoch 5 model with proper configuration"""
    
    # Model path
    model_path = "models/model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth"
    
    # Create argument namespace with the correct parameters
    class Args:
        def __init__(self):
            # Model architecture parameters
            self.dropout_input = 0.1
            self.number_of_classes = 2
            self.alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+ =<>()[]{}"
            self.number_of_characters = 69
            self.extra_characters = "éàèùâêîôûçëïü"
            self.max_length = 1500  # This matches the model filename
            self.steps = ["lower"]
            
            # Model architecture (small configuration from config.json)
            self.conv_layers = [
                [256, 7, 3],
                [256, 7, 3], 
                [256, 3, -1],
                [256, 3, -1],
                [256, 3, -1],
                [256, 3, 3]
            ]
            self.fc_layers = [1024, 1024]
    
    args = Args()
    
    # Check if CUDA is available
    use_cuda = torch.cuda.is_available()
    device = "cuda" if use_cuda else "cpu"
    print(f"Using device: {device}")
    
    # Load the model
    print(f"Loading model from: {model_path}")
    model = CharacterLevelCNN(args, args.number_of_classes)
    
    # Load the trained weights
    if os.path.exists(model_path):
        state = torch.load(model_path, map_location=device)
        model.load_state_dict(state)
        model.eval()
        
        if use_cuda:
            model = model.to("cuda")
        
        print("Model loaded successfully!")
        return model, args, device
    else:
        raise FileNotFoundError(f"Model file not found: {model_path}")

def predict_text(model, args, device, text):
    """Make a prediction on the given text"""
    
    # Set the text in args for preprocessing
    args.text = text
    
    # Preprocess the input
    processed_input = utils.preprocess_input(args)
    processed_input = torch.tensor(processed_input)
    processed_input = processed_input.unsqueeze(0)
    
    if device == "cuda":
        processed_input = processed_input.to("cuda")
    
    # Make prediction
    with torch.no_grad():
        prediction = model(processed_input)
        probabilities = F.softmax(prediction, dim=1)
        probabilities = probabilities.detach().cpu().numpy()
    
    return probabilities

def main():
    """Main function to run the epoch 5 model"""
    
    parser = argparse.ArgumentParser(description="Run the epoch 5 CNN model for text classification")
    parser.add_argument("--text", type=str, default="I love this movie!", 
                       help="Text to classify (default: 'I love this movie!')")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run in interactive mode")
    
    cmd_args = parser.parse_args()
    
    try:
        # Load the model
        model, args, device = load_epoch5_model()
        
        if cmd_args.interactive:
            print("\n=== Interactive Mode ===")
            print("Enter text to classify (type 'quit' to exit):")
            
            while True:
                text = input("\nEnter text: ").strip()
                if text.lower() == 'quit':
                    break
                
                if text:
                    probabilities = predict_text(model, args, device, text)
                    print(f"Input: {text}")
                    print(f"Prediction [Human, AI]: {probabilities[0]}")
                    
                    # Interpret the results
                    if probabilities[0][0] > probabilities[0][1]:
                        print(f"Classification: Human-written (confidence: {probabilities[0][0]:.4f})")
                    else:
                        print(f"Classification: AI-generated (confidence: {probabilities[0][1]:.4f})")
        else:
            # Single prediction mode
            text = cmd_args.text
            probabilities = predict_text(model, args, device, text)
            
            print(f"\n=== Epoch 5 Model Prediction ===")
            print(f"Input: {text}")
            print(f"Prediction [Human, AI]: {probabilities[0]}")
            
            # Interpret the results
            if probabilities[0][0] > probabilities[0][1]:
                print(f"Classification: Human-written (confidence: {probabilities[0][0]:.4f})")
            else:
                print(f"Classification: AI-generated (confidence: {probabilities[0][1]:.4f})")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())