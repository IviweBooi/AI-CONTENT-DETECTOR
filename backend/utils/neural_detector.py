import os
import sys
from typing import Dict, List, Union
from datetime import datetime
from .confidence_tuner import ConfidenceTuner, ThresholdConfig

# Add predictor_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor_model'))

try:
    from predictor_model.ai_text_classifier import AITextClassifier
    MODEL_AVAILABLE = True
except ImportError as e:
    # Warning: Could not import trained model: {e}
    MODEL_AVAILABLE = False

class NeuralAIDetector:
    """
    Neural-only AI content detector using RoBERTa model for accurate detection.
    """
    
    def __init__(self, model_path=None, threshold_config=None):
        """
        Initialize the neural detector.
        
        Args:
            model_path (str): Path to the trained model checkpoint
            threshold_config (ThresholdConfig): Custom threshold configuration for confidence tuning
        """
        # Initialize confidence tuner
        self.confidence_tuner = ConfidenceTuner(threshold_config)
        
        # Initialize neural model
        self.neural_model = None
        if MODEL_AVAILABLE:
            try:
                if model_path is None:
                    # Use the working roberta-base-openai-detector model
                    self.neural_model = AITextClassifier("roberta-base-openai-detector")
                else:
                    self.neural_model = AITextClassifier(model_path)
            except Exception as e:
                # Warning: Could not load neural model: {e}
                self.neural_model = None
        
        # Confidence thresholds for different classification levels
        self.confidence_thresholds = {
            'very_high': 0.9,
            'high': 0.75,
            'medium': 0.6,
            'low': 0.4,
            'very_low': 0.2
        }
    
    def detect(self, text: str) -> Dict[str, Union[str, float, List, Dict]]:
        """
        Perform AI detection using the neural model (RoBERTa).
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            dict: Neural model analysis results
        """
        if not text or not text.strip():
            return self._create_error_response('Empty text provided')
        
        # Get prediction from neural model
        neural_result = self._get_neural_prediction(text)
        
        if not neural_result['available']:
            return self._create_error_response(neural_result.get('error', 'Neural model not available'))
        
        # Create result using neural model prediction
        return self._create_neural_result(neural_result, text)
    
    def _get_neural_prediction(self, text: str) -> Dict[str, Union[float, str, bool]]:
        """
        Get prediction from neural model.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Neural model prediction results
        """
        if self.neural_model is None:
            return {
                'available': False,
                'ai_probability': 0.5,
                'confidence': 0.0,
                'error': 'Neural model not available'
            }
        
        try:
            result = self.neural_model.predict(text)
            return {
                'available': True,
                'ai_probability': result['ai_probability'],
                'human_probability': result['human_probability'],
                'confidence': result['confidence'],
                'error': None
            }
        except Exception as e:
            return {
                'available': False,
                'ai_probability': 0.5,
                'confidence': 0.0,
                'error': f'Neural model error: {str(e)}'
            }
    
    def _create_neural_result(self, neural_result: Dict, text: str) -> Dict[str, Union[str, float, List, Dict]]:
        """
        Create result using neural model prediction.
        
        Args:
            neural_result (dict): Neural model prediction
            text (str): Original text
            
        Returns:
            dict: Neural detection result
        """
        ai_probability = neural_result['ai_probability']
        human_probability = neural_result.get('human_probability', 1.0 - ai_probability)
        confidence = neural_result['confidence']
        
        # Use confidence tuner for classification
        classification_result = self.confidence_tuner.classify_with_confidence(
            ai_probability, confidence
        )
        classification = classification_result['classification']
        risk_level = classification_result['risk_level']
        confidence_indicator = classification_result['confidence_indicators']
        
        # Generate feedback messages
        feedback_messages = self._generate_feedback_messages(ai_probability, confidence, text)
        
        return {
            'ai_probability': round(ai_probability, 3),
            'human_probability': round(human_probability, 3),
            'confidence': round(confidence, 3),
            'classification': classification,
            'risk_level': risk_level,
            'confidence_indicator': confidence_indicator,
            'method_info': {
                'prediction_method': 'neural_only',
                'model_used': 'roberta-base-openai-detector',
                'neural_prediction': round(ai_probability, 3)
            },
            'analysis': {
                'prediction_method': 'neural_only',
                'text_length': len(text),
                'model_confidence': round(confidence, 3),
                'detection_method': 'neural_only'
            },
            'feedback_messages': feedback_messages,
            'timestamp': datetime.now().isoformat(),
            'detection_method': 'neural_only'
        }
    
    def _generate_feedback_messages(self, ai_prob: float, confidence: float, text: str) -> List[str]:
        """
        Generate feedback messages based on neural analysis.
        
        Args:
            ai_prob (float): AI probability
            confidence (float): Model confidence
            text (str): Original text
            
        Returns:
            list: Feedback messages
        """
        messages = []
        
        # Main classification message
        if ai_prob > 0.7:
            messages.append(f"🤖 High likelihood of AI-generated content ({ai_prob:.1%} confidence)")
        elif ai_prob > 0.5:
            messages.append(f"⚠️ Moderate likelihood of AI-generated content ({ai_prob:.1%} confidence)")
        else:
            messages.append(f"👤 Likely human-written content ({(1-ai_prob):.1%} confidence)")
        
        # Confidence-based messages
        if confidence > 0.8:
            messages.append("✅ High model confidence in this prediction")
        elif confidence > 0.6:
            messages.append("📊 Moderate model confidence in this prediction")
        else:
            messages.append("⚠️ Lower model confidence - consider additional review")
        
        # Text length considerations
        if len(text) < 50:
            messages.append("📝 Short text may limit detection accuracy")
        elif len(text) > 2000:
            messages.append("📄 Long text provides more context for accurate detection")
        
        # Model-specific insights
        messages.append("🧠 Analysis based on RoBERTa neural model trained on AI/human text patterns")
        
        return messages
    
    def _create_error_response(self, error_message: str) -> Dict[str, Union[str, float, List]]:
        """
        Create standardized error response.
        
        Args:
            error_message (str): Error description
            
        Returns:
            dict: Error response
        """
        return {
            'error': True,
            'message': error_message,
            'ai_probability': 0.5,
            'human_probability': 0.5,
            'confidence': 0.0,
            'classification': 'unknown',
            'risk_level': 'unknown',
            'method_info': {
                'prediction_method': 'neural_only',
                'model_used': 'roberta-base-openai-detector',
                'status': 'error'
            },
            'feedback_messages': [f"❌ Error: {error_message}"],
            'timestamp': datetime.now().isoformat()
        }

def detect_ai_content_neural(text: str, model_path: str = None) -> Dict[str, Union[str, float, List, Dict]]:
    """
    Perform neural-only AI detection on text.
    
    Args:
        text (str): Text to analyze
        model_path (str): Optional path to model checkpoint
        
    Returns:
        dict: Neural detection results
    """
    detector = NeuralAIDetector(model_path=model_path)
    return detector.detect(text)