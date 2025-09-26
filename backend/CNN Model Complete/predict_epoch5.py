import argparse
import torch
import torch.nn.functional as F
import sys
import os

# Add the character-based-cnn-master directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'character-based-cnn-master'))

from src.model import CharacterLevelCNN
from src import utils

use_cuda = torch.cuda.is_available()


def predict(args):
    model = CharacterLevelCNN(args, args.number_of_classes)
    state = torch.load(args.model, map_location='cpu' if not use_cuda else 'cuda')
    model.load_state_dict(state)
    model.eval()

    processed_input = utils.preprocess_input(args)
    processed_input = torch.tensor(processed_input)
    processed_input = processed_input.unsqueeze(0)
    if use_cuda:
        processed_input = processed_input.to("cuda")
        model = model.to("cuda")
    prediction = model(processed_input)
    probabilities = F.softmax(prediction, dim=1)
    probabilities = probabilities.detach().cpu().numpy()
    return probabilities


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Testing the Epoch 5 Character Based CNN for text classification"
    )
    
    parser.add_argument("--dropout_input", type=float, default=0.1)
    parser.add_argument("--model", type=str, default="models/model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth", help="path for pre-trained model")
    parser.add_argument("--text", type=str, default="I love this movie!", help="text string")
    parser.add_argument("--steps", nargs="+", default=["lower"])

    # Exact configuration that matches the epoch 5 model training
    parser.add_argument(
        "--alphabet",
        type=str,
        default="abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+ =<>()[]{}", 
    )
    parser.add_argument("--number_of_characters", type=int, default=69)
    parser.add_argument("--extra_characters", type=str, default="")  # No extra characters for epoch 5 model
    parser.add_argument("--max_length", type=int, default=1500)
    parser.add_argument("--number_of_classes", type=int, default=2)

    args = parser.parse_args()
    
    print(f"Using device: {'CUDA' if use_cuda else 'CPU'}")
    print(f"Model: {args.model}")
    print(f"Input text: {args.text}")
    print(f"Alphabet size: {args.number_of_characters + len(args.extra_characters)}")
    print()
    
    try:
        prediction = predict(args)
        
        print("=== Epoch 5 Model Results ===")
        print(f"Input: {args.text}")
        print(f"Prediction [Human, AI]: {prediction[0]}")
        
        # Interpret the results
        human_prob = prediction[0][0]
        ai_prob = prediction[0][1]
        
        if human_prob > ai_prob:
            print(f"Classification: Human-written (confidence: {human_prob:.4f})")
        else:
            print(f"Classification: AI-generated (confidence: {ai_prob:.4f})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()