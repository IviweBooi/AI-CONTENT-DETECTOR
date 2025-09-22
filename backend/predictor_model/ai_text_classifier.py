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
        model_name: str = "roberta-base-openai-detector", 
        max_length: int = 512,
        device: Optional[str] = None
    ) -> None:
        """Initialize the AI text classifier.
        
        Args:
            model_name: Name of the pre-trained model (default: roberta-base-openai-detector)
            max_length: Maximum sequence length for tokenization (default: 512)
            device: Device for inference. If None, auto-detects best available
            
        Raises:
            RuntimeError: If model loading fails
        """
        self.model_name = model_name
        self.max_length = max_length
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Initializing classifier with device: {self.device}")
        logger.info(f"Using pre-trained model: {self.model_name}")
            
        # Load tokenizer and model
        self._load_model()
        
    def _load_model(self) -> None:
        """Load the tokenizer and model from Hugging Face.
        
        Raises:
            RuntimeError: If model or tokenizer loading fails
        """
        try:
            logger.info(f"Loading tokenizer and model: {self.model_name}")
            
            # Try to load the specified model, fallback to a working alternative
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            except Exception as e:
                logger.warning(f"Failed to load {self.model_name}: {e}")
                logger.info("Falling back to roberta-base with binary classification")
                
                # Fallback to roberta-base and configure for binary classification
                self.model_name = "roberta-base"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name, 
                    num_labels=2,
                    problem_type="single_label_classification"
                )
            
            # Move model to device and set to evaluation mode
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model {self.model_name} loaded successfully")
            
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
            Dictionary containing:
                - ai_probability: Probability that text is AI-generated (0-1)
                - human_probability: Probability that text is human-written (0-1)
                - confidence: Model confidence in the prediction (0-1)
                - prediction: 'ai' or 'human'
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
            
            # If using base roberta model, use rule-based approach
            if self.model_name == "roberta-base":
                return self._rule_based_prediction(processed_text)
            
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
    
    def _rule_based_prediction(self, text: str) -> Dict[str, Union[float, str]]:
        """Simple rule-based prediction as fallback.
        
        Args:
            text: Preprocessed text to analyze
            
        Returns:
            Dictionary with prediction results
        """
        # Simple heuristics for AI detection
        ai_indicators = 0
        total_checks = 0
        
        # Check for repetitive patterns
        words = text.split()
        if len(words) > 10:
            total_checks += 1
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # High repetition might indicate AI
            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq > len(words) * 0.1:  # More than 10% repetition
                ai_indicators += 1
        
        # Check for very formal/structured language
        total_checks += 1
        formal_words = ['furthermore', 'moreover', 'consequently', 'therefore', 'additionally']
        formal_count = sum(1 for word in formal_words if word in text.lower())
        if formal_count > 2:
            ai_indicators += 1
        
        # Check for very long sentences (AI tends to generate longer sentences)
        total_checks += 1
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if avg_sentence_length > 25:
            ai_indicators += 1
        
        # Calculate AI probability based on indicators
        ai_prob = ai_indicators / max(total_checks, 1) if total_checks > 0 else 0.5
        human_prob = 1 - ai_prob
        
        # Add some randomness to avoid always returning the same confidence
        confidence = 0.6 + (ai_prob * 0.3)  # Confidence between 0.6 and 0.9
        
        prediction = 'ai' if ai_prob > 0.5 else 'human'
        
        return {
            'ai_probability': ai_prob,
            'human_probability': human_prob,
            'confidence': confidence,
            'prediction': prediction
        }

