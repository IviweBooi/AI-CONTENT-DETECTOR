import os
import sys
import torch
import torch.nn.functional as F
import numpy as np
import re
from typing import Dict, Any, Tuple

# Add the CNN model directory to the path
cnn_model_path = os.path.join(os.path.dirname(__file__), '..', 'CNN Model Complete', 'character-based-cnn-master')
sys.path.append(cnn_model_path)

try:
    from src.model import CharacterLevelCNN
    from src import utils
    CNN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CNN model dependencies not available: {e}")
    CNN_AVAILABLE = False


class CNNTextClassifier:
    """
    CNN-based AI text classifier that maintains compatibility with the existing AITextClassifier interface.
    Uses character-level CNN for detecting AI-generated content.
    """
    
    def __init__(self, model_path: str = None, device: str = "auto"):
        """
        Initialize the CNN text classifier.
        
        Args:
            model_path: Path to the trained CNN model file
            device: Device to run the model on ("auto", "cuda", or "cpu")
        """
        self.device = self._get_device(device)
        self.model = None
        self.model_loaded = False
        
        # CNN model configuration (matching the epoch 5 model)
        self.config = {
            'dropout_input': 0.1,
            'alphabet': "abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+ =<>()[]{}",
            'number_of_characters': 69,
            'extra_characters': "",
            'max_length': 1500,
            'number_of_classes': 2,
            'steps': ["lower"]
        }
        
        # Set default model path
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'CNN Model Complete', 
                'models', 
                'model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth'
            )
        
        self.model_path = model_path
        
        # Load the model
        if CNN_AVAILABLE:
            self._load_model()
        else:
            print("Warning: CNN model not available, falling back to rule-based detection")
    
    def _get_device(self, device: str) -> str:
        """Determine the appropriate device for model execution."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _load_model(self):
        """Load the CNN model from the specified path."""
        try:
            if not os.path.exists(self.model_path):
                print(f"Warning: CNN model file not found at {self.model_path}")
                return
            
            # Create model instance
            class Args:
                def __init__(self, config):
                    for key, value in config.items():
                        setattr(self, key, value)
            
            args = Args(self.config)
            self.model = CharacterLevelCNN(args, self.config['number_of_classes'])
            
            # Load model weights
            state = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state)
            self.model.eval()
            
            # Move model to device
            if self.device == "cuda":
                self.model = self.model.to("cuda")
            
            self.model_loaded = True
            print(f"CNN model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading CNN model: {e}")
            self.model_loaded = False
    
    def _preprocess_text(self, text: str) -> np.ndarray:
        """
        Preprocess text for CNN model input.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text as numpy array
        """
        # Apply preprocessing steps
        processed_text = text
        for step in self.config['steps']:
            if step == "lower":
                processed_text = processed_text.lower()
            elif step == "remove_urls":
                processed_text = re.sub(r"^https?:\/\/.*[\r\n]*", "", processed_text, flags=re.MULTILINE)
            elif step == "remove_hashtags":
                processed_text = re.sub(r"#[A-Za-z0-9_]+", "", processed_text)
            elif step == "remove_user_mentions":
                processed_text = re.sub(r"@[A-Za-z0-9_]+", "", processed_text)
        
        # Character-level encoding
        number_of_characters = self.config['number_of_characters'] + len(self.config['extra_characters'])
        identity_mat = np.identity(number_of_characters)
        vocabulary = list(self.config['alphabet']) + list(self.config['extra_characters'])
        max_length = self.config['max_length']
        
        # Convert text to character indices (reversed)
        processed_output = np.array(
            [
                identity_mat[vocabulary.index(i)]
                for i in list(processed_text[::-1])
                if i in vocabulary
            ],
            dtype=np.float32,
        )
        
        # Handle length constraints
        if len(processed_output) > max_length:
            processed_output = processed_output[:max_length]
        elif 0 < len(processed_output) < max_length:
            processed_output = np.concatenate(
                (
                    processed_output,
                    np.zeros(
                        (max_length - len(processed_output), number_of_characters),
                        dtype=np.float32,
                    ),
                )
            )
        elif len(processed_output) == 0:
            processed_output = np.zeros(
                (max_length, number_of_characters), dtype=np.float32
            )
        
        return processed_output
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict whether text is AI-generated or human-written.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary containing prediction results matching AITextClassifier format
        """
        if not self.model_loaded or not CNN_AVAILABLE:
            return self._rule_based_prediction(text)
        
        try:
            # Preprocess text
            processed_input = self._preprocess_text(text)
            processed_input = torch.tensor(processed_input).unsqueeze(0)
            
            # Move to device
            if self.device == "cuda":
                processed_input = processed_input.to("cuda")
            
            # Get prediction
            with torch.no_grad():
                prediction = self.model(processed_input)
                probabilities = F.softmax(prediction, dim=1)
                probabilities = probabilities.detach().cpu().numpy()[0]
            
            # Extract probabilities
            human_prob = float(probabilities[0])
            ai_prob = float(probabilities[1])
            
            # Determine prediction and confidence
            if ai_prob > human_prob:
                prediction_label = "AI"
                confidence = ai_prob
            else:
                prediction_label = "Human"
                confidence = human_prob
            
            return {
                "prediction": prediction_label,
                "confidence": confidence,
                "ai_probability": ai_prob,
                "human_probability": human_prob,
                "probabilities": [human_prob, ai_prob],
                "model_type": "CNN"
            }
            
        except Exception as e:
            print(f"Error during CNN prediction: {e}")
            return self._rule_based_prediction(text)
    
    def _rule_based_prediction(self, text: str) -> Dict[str, Any]:
        """
        Fallback rule-based prediction when CNN model is not available.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary containing prediction results
        """
        # Simple heuristics for fallback
        text_lower = text.lower()
        
        # AI indicators
        ai_indicators = [
            "as an ai", "i'm an ai", "artificial intelligence", "language model",
            "i don't have personal", "i cannot", "i'm not able to",
            "furthermore", "moreover", "additionally", "in conclusion"
        ]
        
        ai_score = sum(1 for indicator in ai_indicators if indicator in text_lower)
        
        # Length and structure analysis
        sentences = text.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Adjust score based on structure
        if avg_sentence_length > 20:  # Very long sentences might indicate AI
            ai_score += 0.5
        
        # Normalize score
        ai_probability = min(0.8, ai_score * 0.2 + 0.1)  # Cap at 80%
        human_probability = 1.0 - ai_probability
        
        prediction_label = "AI" if ai_probability > 0.5 else "Human"
        confidence = max(ai_probability, human_probability)
        
        return {
            "prediction": prediction_label,
            "confidence": confidence,
            "ai_probability": ai_probability,
            "human_probability": human_probability,
            "probabilities": [human_probability, ai_probability],
            "model_type": "Rule-based (CNN fallback)"
        }


# For backward compatibility and testing
if __name__ == "__main__":
    # Test the CNN classifier
    classifier = CNNTextClassifier()
    
    test_texts = [
        "I love this movie! It's absolutely fantastic and made me cry.",
        "As an AI language model, I can provide you with comprehensive information about this topic.",
        "Hey guys! Just wanted to share my experience with this new restaurant downtown."
    ]
    
    for text in test_texts:
        result = classifier.predict(text)
        print(f"Text: {text[:50]}...")
        print(f"Prediction: {result['prediction']} (Confidence: {result['confidence']:.3f})")
        print(f"AI Prob: {result['ai_probability']:.3f}, Human Prob: {result['human_probability']:.3f}")
        print(f"Model: {result['model_type']}")
        print("-" * 50)