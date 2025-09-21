"""AI Text Classifier Module

This module provides a robust text classification system for detecting AI-generated content
using a fine-tuned RoBERTa model. The classifier includes comprehensive preprocessing,
error handling, and confidence scoring.

Author: The Detect3rs
Version: 1.0.0
"""

import re
import logging
from pathlib import Path
from typing import Dict, Union, Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AITextClassifier:
    """A robust text classifier for detecting AI-generated content.
    
    This class loads a pre-trained sequence classification model and provides
    methods to predict whether given text is AI-generated or human-written.
    
    Attributes:
        model_path (str): Path to the trained model checkpoint
        tokenizer_name (str): Name of the tokenizer to use
        max_length (int): Maximum sequence length for tokenization
        device (str): Device to run inference on (cpu/cuda)
    """
    
    def __init__(
        self, 
        model_path: str = "checkpoint-120", 
        tokenizer_name: str = "roberta-base",
        max_length: int = 512,
        device: Optional[str] = None
    ) -> None:
        """Initialize the AI text classifier.
        
        Args:
            model_path: Path to the trained model checkpoint
            tokenizer_name: Name of the base tokenizer (default: roberta-base)
            max_length: Maximum sequence length for tokenization (default: 256)
            device: Device for inference. If None, auto-detects best available
            
        Raises:
            FileNotFoundError: If model path doesn't exist
            RuntimeError: If model loading fails
        """
        self.model_path = Path(model_path)
        self.tokenizer_name = tokenizer_name
        self.max_length = max_length
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Initializing classifier with device: {self.device}")
        
        # Validate model path
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")
            
        # Load tokenizer and model
        self._load_model()
        
    def _load_model(self) -> None:
        """Load the tokenizer and model from the specified paths.
        
        Raises:
            RuntimeError: If model or tokenizer loading fails
        """
        try:
            logger.info(f"Loading tokenizer: {self.tokenizer_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
            
            logger.info(f"Loading model from: {self.model_path}")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                str(self.model_path)
            )
            
            # Move model to device and set to evaluation mode
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def _preprocess_text(self, text: str) -> str:
        """Apply comprehensive text preprocessing.
        
        This preprocessing matches the steps applied during training
        to ensure consistent model performance.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text:
            return ""
            
        # Normalize quotes to single quotes
        text = text.replace('"', "'")
         
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def predict(self, text: str) -> Dict[str, Union[float, str]]:
        """Predict whether the given text is AI-generated or human-written.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary containing prediction results with probabilities and confidence
        """
        if not text or not text.strip():
            return {
                'ai_probability': 0.0,
                'human_probability': 1.0,
                'confidence': 0.0,
                'prediction': 'human'
            }
        
        try:
            # Preprocess the text
            processed_text = self._preprocess_text(text)
            
            # Tokenize the input
            inputs = self.tokenizer(
                processed_text,
                return_tensors="pt",
                truncation=True,
                padding="max_length",
                max_length=self.max_length
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Apply softmax to get probabilities
                probabilities = torch.softmax(logits, dim=-1)
                
                # Extract probabilities for each class
                human_prob = probabilities[0][0].item()  # Class 0: human
                ai_prob = probabilities[0][1].item()     # Class 1: ai
                
                # Calculate confidence as the maximum probability
                confidence = max(human_prob, ai_prob)
                
                # Determine prediction
                prediction = 'ai' if ai_prob > human_prob else 'human'
                
                return {
                    'ai_probability': ai_prob,
                    'human_probability': human_prob,
                    'confidence': confidence,
                    'prediction': prediction
                }
                
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {
                'ai_probability': 0.0,
                'human_probability': 1.0,
                'confidence': 0.0,
                'prediction': 'error',
                'error': str(e)
            }

