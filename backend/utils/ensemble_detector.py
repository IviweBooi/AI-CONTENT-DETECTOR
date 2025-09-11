import os
import sys
from typing import Dict, List, Union, Tuple
import numpy as np
from datetime import datetime
from .confidence_tuner import ConfidenceTuner, ThresholdConfig

# Add predictor_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor_model'))

try:
    from predictor_model.ai_text_classifier import AITextClassifier
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import trained model: {e}")
    MODEL_AVAILABLE = False

from rule_based_detector import RuleBasedAIDetector

class EnsembleAIDetector:
    """
    Ensemble AI content detector that combines neural model predictions with rule-based analysis
    for improved accuracy and reliability.
    """
    
    def __init__(self, model_path=None, ensemble_weights=None, threshold_config=None):
        """
        Initialize the ensemble detector.
        
        Args:
            model_path (str): Path to the trained model checkpoint
            ensemble_weights (dict): Weights for combining different detection methods
            threshold_config (ThresholdConfig): Custom threshold configuration for confidence tuning
        """
        # Initialize confidence tuner
        self.confidence_tuner = ConfidenceTuner(threshold_config)
        
        # Initialize rule-based detector (always available)
        self.rule_detector = RuleBasedAIDetector()
        
        # Initialize neural model if available
        self.neural_model = None
        if MODEL_AVAILABLE:
            try:
                if model_path is None:
                    model_path = os.path.join(os.path.dirname(__file__), '..', 'predictor_model', 'checkpoint-120')
                self.neural_model = AITextClassifier(model_path)
            except Exception as e:
                print(f"Warning: Could not load neural model: {e}")
                self.neural_model = None
        
        # Default ensemble weights
        self.weights = ensemble_weights or {
            'neural_model': 0.7,  # Primary weight for neural model
            'rule_based': 0.3,    # Secondary weight for rule-based
            'confidence_boost': 0.1  # Boost when both methods agree
        }
        
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
        Perform ensemble AI detection combining neural and rule-based methods.
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            dict: Comprehensive analysis results
        """
        if not text or not text.strip():
            return self._create_error_response('Empty text provided')
        
        # Get predictions from both methods
        neural_result = self._get_neural_prediction(text)
        rule_result = self._get_rule_based_prediction(text)
        
        # Combine predictions using ensemble method
        ensemble_result = self._combine_predictions(neural_result, rule_result, text)
        
        return ensemble_result
    
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
                'ai_probability': 0.5,  # Neutral when unavailable
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
    
    def _get_rule_based_prediction(self, text: str) -> Dict[str, Union[float, str, bool, List]]:
        """
        Get prediction from rule-based detector.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Rule-based prediction results
        """
        try:
            result = self.rule_detector.analyze_text(text)
            return {
                'available': True,
                'ai_probability': result['ai_probability'],
                'confidence': result['confidence'],
                'features': result['features'],
                'flags': result['flags'],
                'reasoning': result['reasoning'],
                'error': None
            }
        except Exception as e:
            return {
                'available': False,
                'ai_probability': 0.5,
                'confidence': 0.0,
                'error': f'Rule-based detector error: {str(e)}'
            }
    
    def _combine_predictions(self, neural_result: Dict, rule_result: Dict, text: str) -> Dict[str, Union[str, float, List, Dict]]:
        """
        Combine neural and rule-based predictions using ensemble method.
        
        Args:
            neural_result (dict): Neural model results
            rule_result (dict): Rule-based results
            text (str): Original text
            
        Returns:
            dict: Combined ensemble results
        """
        # Determine which methods are available
        neural_available = neural_result.get('available', False)
        rule_available = rule_result.get('available', False)
        
        if not neural_available and not rule_available:
            return self._create_error_response('Both detection methods failed')
        
        # Calculate ensemble AI probability
        if neural_available and rule_available:
            # Both methods available - use weighted combination
            neural_prob = neural_result['ai_probability']
            rule_prob = rule_result['ai_probability']
            
            # Base ensemble probability
            ensemble_prob = (
                neural_prob * self.weights['neural_model'] + 
                rule_prob * self.weights['rule_based']
            )
            
            # Agreement bonus: boost confidence when both methods agree
            agreement = 1 - abs(neural_prob - rule_prob)
            if agreement > 0.7:  # Strong agreement
                confidence_boost = self.weights['confidence_boost'] * agreement
                if neural_prob > 0.5 and rule_prob > 0.5:  # Both predict AI
                    ensemble_prob = min(1.0, ensemble_prob + confidence_boost)
                elif neural_prob < 0.5 and rule_prob < 0.5:  # Both predict human
                    ensemble_prob = max(0.0, ensemble_prob - confidence_boost)
            
            # Calculate ensemble confidence
            neural_conf = neural_result.get('confidence', 0.5)
            rule_conf = rule_result.get('confidence', 0.5)
            base_confidence = (neural_conf * self.weights['neural_model'] + 
                             rule_conf * self.weights['rule_based'])
            
            # Boost confidence based on agreement
            ensemble_confidence = min(0.95, base_confidence + (agreement * 0.2))
            
            method_info = {
                'neural_prediction': neural_prob,
                'rule_prediction': rule_prob,
                'agreement_score': agreement,
                'method': 'ensemble'
            }
            
        elif neural_available:
            # Only neural model available
            ensemble_prob = neural_result['ai_probability']
            ensemble_confidence = neural_result.get('confidence', 0.5) * 0.8  # Reduce confidence
            method_info = {
                'neural_prediction': ensemble_prob,
                'rule_prediction': None,
                'method': 'neural_only',
                'note': 'Rule-based detection unavailable'
            }
            
        else:
            # Only rule-based available
            ensemble_prob = rule_result['ai_probability']
            ensemble_confidence = rule_result.get('confidence', 0.5) * 0.9  # Slight reduction
            method_info = {
                'neural_prediction': None,
                'rule_prediction': ensemble_prob,
                'method': 'rule_only',
                'note': 'Neural model unavailable'
            }
        
        # Use confidence tuner for enhanced classification
        tuned_result = self.confidence_tuner.classify_with_confidence(
            ai_probability=ensemble_prob,
            neural_confidence=neural_result.get('confidence') if neural_available else None,
            rule_confidence=rule_result.get('confidence') if rule_available else None,
            text_length=len(text)
        )
        
        # Generate comprehensive feedback
        feedback = self._generate_ensemble_feedback(
            ensemble_prob, tuned_result['confidence'], neural_result, rule_result, text
        )
        
        # Compile final result
        result = {
            'ai_probability': round(ensemble_prob, 3),
            'human_probability': round(1 - ensemble_prob, 3),
            'confidence': round(tuned_result['confidence'], 3),
            'classification': tuned_result['classification'],
            'risk_level': tuned_result['risk_level'],
            'confidence_indicators': tuned_result['confidence_indicators'],
            'method_info': method_info,
            'analysis': {
                'word_count': len(text.split()),
                'sentence_count': len([s for s in text.split('.') if s.strip()]),
                'detection_method': 'ensemble',
                'timestamp': datetime.now().isoformat()
            },
            'feedback_messages': feedback['messages'],
            'flagged_sections': feedback['flagged_sections'],
            'recommendations': feedback['recommendations'],
            'threshold_info': tuned_result['threshold_info']
        }
        
        # Add detailed breakdowns if available
        if rule_available and 'features' in rule_result:
            result['rule_based_analysis'] = {
                'features': rule_result['features'],
                'flags': rule_result.get('flags', []),
                'reasoning': rule_result.get('reasoning', [])
            }
        
        if neural_available:
            result['neural_analysis'] = {
                'confidence': neural_result.get('confidence', 0),
                'available': True
            }
        
        return result
    
    def _classify_result(self, ai_prob: float, confidence: float) -> Tuple[str, str]:
        """
        Classify the result based on AI probability and confidence.
        
        Args:
            ai_prob (float): AI probability
            confidence (float): Confidence score
            
        Returns:
            tuple: (classification, risk_level)
        """
        # Adjust thresholds based on confidence
        if confidence < 0.5:
            # Lower confidence - be more conservative
            if ai_prob >= 0.8:
                classification = 'Likely AI-Generated'
                risk_level = 'High'
            elif ai_prob >= 0.6:
                classification = 'Possibly AI-Generated'
                risk_level = 'Medium'
            elif ai_prob >= 0.4:
                classification = 'Uncertain'
                risk_level = 'Medium'
            elif ai_prob >= 0.2:
                classification = 'Possibly Human-Written'
                risk_level = 'Low'
            else:
                classification = 'Likely Human-Written'
                risk_level = 'Very Low'
        else:
            # Higher confidence - use standard thresholds
            if ai_prob >= 0.85:
                classification = 'Highly Likely AI-Generated'
                risk_level = 'Very High'
            elif ai_prob >= 0.7:
                classification = 'Likely AI-Generated'
                risk_level = 'High'
            elif ai_prob >= 0.5:
                classification = 'Possibly AI-Generated'
                risk_level = 'Medium'
            elif ai_prob >= 0.3:
                classification = 'Likely Human-Written'
                risk_level = 'Low'
            else:
                classification = 'Highly Likely Human-Written'
                risk_level = 'Very Low'
        
        return classification, risk_level
    
    def _generate_ensemble_feedback(self, ai_prob: float, confidence: float, 
                                  neural_result: Dict, rule_result: Dict, text: str) -> Dict[str, List]:
        """
        Generate comprehensive feedback based on ensemble analysis.
        
        Args:
            ai_prob (float): Ensemble AI probability
            confidence (float): Ensemble confidence
            neural_result (dict): Neural model results
            rule_result (dict): Rule-based results
            text (str): Original text
            
        Returns:
            dict: Feedback messages, flagged sections, and recommendations
        """
        messages = []
        flagged_sections = []
        recommendations = []
        
        # Method availability messages
        neural_available = neural_result.get('available', False)
        rule_available = rule_result.get('available', False)
        
        if neural_available and rule_available:
            agreement = 1 - abs(neural_result['ai_probability'] - rule_result['ai_probability'])
            if agreement > 0.8:
                messages.append("🎯 High agreement between neural and rule-based detection methods")
            elif agreement > 0.6:
                messages.append("✅ Moderate agreement between detection methods")
            else:
                messages.append("⚠️ Detection methods show different results - review recommended")
        elif neural_available:
            messages.append("🤖 Analysis based on neural model only (rule-based unavailable)")
        elif rule_available:
            messages.append("📋 Analysis based on rule-based detection only (neural model unavailable)")
        
        # AI probability feedback
        if ai_prob >= 0.8:
            messages.append("🚨 High AI probability detected - strong indicators present")
            recommendations.extend([
                "Verify source and authorship carefully",
                "Request additional documentation",
                "Consider manual review by experts"
            ])
        elif ai_prob >= 0.6:
            messages.append("⚠️ Moderate AI probability - some suspicious patterns found")
            recommendations.extend([
                "Conduct additional verification",
                "Review flagged sections carefully",
                "Consider context and purpose"
            ])
        elif ai_prob >= 0.4:
            messages.append("🤔 Uncertain classification - mixed indicators")
            recommendations.extend([
                "Gather additional context",
                "Consider longer text samples",
                "Use multiple detection methods"
            ])
        else:
            messages.append("✅ Low AI probability - appears human-written")
            recommendations.extend([
                "Content likely authentic",
                "Use as baseline for comparison"
            ])
        
        # Confidence feedback
        if confidence < 0.5:
            messages.append("📊 Low confidence - results should be interpreted cautiously")
            recommendations.append("Consider additional analysis methods")
        elif confidence > 0.8:
            messages.append("📊 High confidence in detection results")
        
        # Add rule-based flagged sections if available
        if rule_available and 'flags' in rule_result:
            for flag in rule_result['flags'][:3]:  # Limit to top 3
                flagged_sections.append({
                    'type': 'rule_based_flag',
                    'description': flag,
                    'source': 'rule_based_detector'
                })
        
        # Text length considerations
        word_count = len(text.split())
        if word_count < 50:
            messages.append("📏 Short text - detection accuracy may be limited")
            recommendations.append("Provide longer text samples for better accuracy")
        elif word_count > 500:
            messages.append("📚 Good text length for reliable detection")
        
        # General recommendations
        recommendations.extend([
            "AI detection is probabilistic, not definitive",
            "Combine with human judgment and context",
            "Consider the purpose and stakes of verification"
        ])
        
        return {
            'messages': messages,
            'flagged_sections': flagged_sections,
            'recommendations': recommendations
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Union[str, float, List]]:
        """
        Create a standardized error response.
        
        Args:
            error_message (str): Error description
            
        Returns:
            dict: Error response
        """
        return {
            'error': error_message,
            'ai_probability': 0.0,
            'human_probability': 0.0,
            'confidence': 0.0,
            'classification': 'Error',
            'risk_level': 'Analysis Failed',
            'analysis': {'detection_method': 'error'},
            'feedback_messages': [f'⚠️ {error_message}'],
            'flagged_sections': [],
            'recommendations': ['Check input and try again', 'Contact support if issue persists']
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update ensemble weights for fine-tuning.
        
        Args:
            new_weights (dict): New weight configuration
        """
        self.weights.update(new_weights)
        # Ensure weights sum to approximately 1.0 (excluding confidence_boost)
        total = self.weights['neural_model'] + self.weights['rule_based']
        if total > 0:
            self.weights['neural_model'] /= total
            self.weights['rule_based'] /= total

# Convenience function for easy integration
def detect_ai_content_ensemble(text: str, model_path: str = None) -> Dict[str, Union[str, float, List, Dict]]:
    """
    Perform ensemble AI detection on text.
    
    Args:
        text (str): Text to analyze
        model_path (str): Optional path to neural model
        
    Returns:
        dict: Ensemble detection results
    """
    detector = EnsembleAIDetector(model_path=model_path)
    return detector.detect(text)