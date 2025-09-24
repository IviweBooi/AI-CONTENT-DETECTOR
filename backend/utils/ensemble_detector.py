import os
import sys
from typing import Dict, List, Union, Tuple
import numpy as np
from datetime import datetime
from .confidence_tuner import ConfidenceTuner, ThresholdConfig
from .pattern_detector import PatternDetector

# Add predictor_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor_model'))

try:
    from predictor_model.ai_text_classifier import AITextClassifier
    MODEL_AVAILABLE = True
except ImportError as e:
    # Warning: Could not import trained model: {e}
    MODEL_AVAILABLE = False

# Rule-based detector removed for neural-only operation

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
        
        # Initialize pattern detector (always available)
        self.pattern_detector = PatternDetector()
        
        # Initialize rule-based detector (always available)
        # Rule-based detector removed for neural-only operation
        
        # Initialize neural model if available
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
        
        # Default ensemble weights - adjusted for better pattern influence
        self.weights = ensemble_weights or {
            'neural_model': 0.5,     # Reduced weight for neural model
            'pattern_detector': 0.4,  # Increased weight for pattern-based detection
            'rule_based': 0.1,       # Secondary weight for rule-based
            'confidence_boost': 0.15  # Increased boost when methods agree
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
        Perform AI detection using neural model enhanced with pattern analysis.
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            dict: Enhanced analysis results combining neural and pattern detection
        """
        if not text or not text.strip():
            return self._create_error_response('Empty text provided')

        # Get predictions from both neural model and pattern detector
        neural_result = self._get_neural_prediction(text)
        pattern_result = self._get_pattern_prediction(text)
        
        # Create enhanced result combining both methods
        enhanced_result = self._create_enhanced_result(neural_result, pattern_result, text)
        
        return enhanced_result
    
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
    
    def _get_pattern_prediction(self, text: str) -> Dict[str, Union[float, str, bool, List]]:
        """
        Get prediction from pattern detector.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Pattern detection results
        """
        try:
            result = self.pattern_detector.analyze_text(text)
            return {
                'available': True,
                'ai_probability': result['ai_probability'],
                'human_probability': result['human_probability'],
                'confidence': result['confidence'],
                'patterns_detected': result['patterns_detected'],
                'analysis': result['analysis'],
                'total_patterns': result['total_patterns'],
                'ai_score': result['ai_score'],
                'human_score': result['human_score'],
                'error': None
            }
        except Exception as e:
            return {
                'available': False,
                'ai_probability': 0.5,
                'confidence': 0.0,
                'patterns_detected': [],
                'error': f'Pattern detector error: {str(e)}'
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
                    'source': 'neural_detector'
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
    
    def _create_neural_only_result(self, neural_result: Dict, text: str) -> Dict[str, Union[str, float, List, Dict]]:
        """
        Create result using only neural model prediction.
        
        Args:
            neural_result (dict): Neural model prediction
            text (str): Original text
            
        Returns:
            dict: Neural-only detection result
        """
        if not neural_result['available']:
            return self._create_error_response('Neural model not available')
        
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
        
        # Generate feedback
        feedback_data = self._generate_ensemble_feedback(ai_probability, confidence, neural_result, {}, text)
        
        return {
            'ai_probability': ai_probability,
            'human_probability': human_probability,
            'confidence': confidence,
            'classification': classification,
            'risk_level': risk_level,
            'confidence_indicator': confidence_indicator,
            'method_info': {
                'prediction_method': 'neural_only',
                'neural_prediction': ai_probability,
                'model_used': 'roberta-base-openai-detector'
            },
            'analysis': {
                'prediction_method': 'neural_only',
                'text_length': len(text),
                'model_confidence': confidence
            },
            'feedback_messages': feedback_data['messages'],
            'flagged_sections': feedback_data['flagged_sections'],
            'recommendations': feedback_data['recommendations']
        }
    
    def _create_enhanced_result(self, neural_result: Dict, pattern_result: Dict, text: str) -> Dict[str, Union[str, float, List, Dict]]:
        """
        Create result combining neural model and pattern detection.
        
        Args:
            neural_result (dict): Neural model prediction
            pattern_result (dict): Pattern detection results
            text (str): Original text
            
        Returns:
            dict: Enhanced detection result
        """
        neural_available = neural_result.get('available', False)
        pattern_available = pattern_result.get('available', False)
        
        if not neural_available and not pattern_available:
            return self._create_error_response('Both neural model and pattern detector failed')
        
        # Calculate combined AI probability
        if neural_available and pattern_available:
            # Both methods available - use dynamic weighted combination
            neural_prob = neural_result['ai_probability']
            pattern_prob = pattern_result['ai_probability']
            
            # Dynamic weighting based on pattern strength
            pattern_strength = self._calculate_pattern_strength(pattern_result)
            
            # Adjust weights based on pattern strength - more aggressive for critical patterns
            if pattern_strength > 0.8:  # Very strong patterns detected
                neural_weight = 0.2
                pattern_weight = 0.8
            elif pattern_strength > 0.6:  # Strong patterns detected
                neural_weight = 0.3
                pattern_weight = 0.7
            elif pattern_strength > 0.4:  # Moderate patterns
                neural_weight = 0.4
                pattern_weight = 0.6
            else:  # Weak patterns - use default weights
                neural_weight = self.weights['neural_model']
                pattern_weight = self.weights['pattern_detector']
            
            # Weighted ensemble with dynamic weights
            combined_prob = (neural_prob * neural_weight + pattern_prob * pattern_weight)
            
            # Critical pattern boost - if very strong patterns detected, boost AI probability
            if pattern_strength > 0.8 and pattern_prob > 0.6:
                critical_boost = min(0.3, pattern_strength * 0.4)  # Up to 30% boost
                combined_prob = min(1.0, combined_prob + critical_boost)
            
            # Agreement bonus
            agreement = 1 - abs(neural_prob - pattern_prob)
            if agreement > 0.6:  # Good agreement
                confidence_boost = self.weights['confidence_boost'] * agreement * 0.5
                if neural_prob > 0.5 and pattern_prob > 0.5:  # Both predict AI
                    combined_prob = min(1.0, combined_prob + confidence_boost)
                elif neural_prob < 0.5 and pattern_prob < 0.5:  # Both predict human
                    combined_prob = max(0.0, combined_prob - confidence_boost)
            
            # Combined confidence using dynamic weights
            neural_conf = neural_result.get('confidence', 0.5)
            pattern_conf = pattern_result.get('confidence', 0.5)
            combined_confidence = (
                neural_conf * neural_weight + 
                pattern_conf * pattern_weight
            )
            # Boost confidence when patterns are strong and methods agree
            pattern_boost = pattern_strength * 0.1 if agreement > 0.6 else 0
            combined_confidence = min(0.95, combined_confidence + (agreement * 0.15) + pattern_boost)
            
            method_info = {
                'prediction_method': 'neural_pattern_ensemble',
                'neural_prediction': neural_prob,
                'pattern_prediction': pattern_prob,
                'agreement_score': agreement,
                'pattern_strength': pattern_strength,
                'neural_weight': neural_weight,
                'pattern_weight': pattern_weight,
                'model_used': 'roberta-base-openai-detector + pattern_analysis'
            }
            
        elif neural_available:
            # Only neural model available
            combined_prob = neural_result['ai_probability']
            combined_confidence = neural_result.get('confidence', 0.5) * 0.85  # Slight reduction
            method_info = {
                'prediction_method': 'neural_only',
                'neural_prediction': combined_prob,
                'pattern_prediction': None,
                'model_used': 'roberta-base-openai-detector',
                'note': 'Pattern detection unavailable'
            }
            
        else:
            # Only pattern detection available
            combined_prob = pattern_result['ai_probability']
            combined_confidence = pattern_result.get('confidence', 0.5) * 0.8  # Reduction for pattern-only
            method_info = {
                'prediction_method': 'pattern_only',
                'neural_prediction': None,
                'pattern_prediction': combined_prob,
                'model_used': 'pattern_analysis',
                'note': 'Neural model unavailable'
            }
        
        # Use confidence tuner for classification
        classification_result = self.confidence_tuner.classify_with_confidence(
            combined_prob, combined_confidence
        )
        
        # Generate enhanced feedback
        feedback_data = self._generate_enhanced_feedback(
            combined_prob, combined_confidence, neural_result, pattern_result, text
        )
        
        # Compile final result
        result = {
            'ai_probability': round(combined_prob, 3),
            'human_probability': round(1 - combined_prob, 3),
            'confidence': round(combined_confidence, 3),
            'classification': classification_result['classification'],
            'risk_level': classification_result['risk_level'],
            'confidence_indicators': classification_result['confidence_indicators'],
            'method_info': method_info,
            'analysis': {
                'prediction_method': method_info['prediction_method'],
                'text_length': len(text),
                'word_count': len(text.split()),
                'sentence_count': len([s for s in text.split('.') if s.strip()]),
                'timestamp': datetime.now().isoformat()
            },
            'feedback_messages': feedback_data['messages'],
            'flagged_sections': feedback_data['flagged_sections'],
            'recommendations': feedback_data['recommendations']
        }
        
        # Add pattern analysis details if available
        if pattern_available:
            result['pattern_analysis'] = {
                'patterns_detected': pattern_result.get('patterns_detected', []),
                'total_patterns': pattern_result.get('total_patterns', 0),
                'ai_score': pattern_result.get('ai_score', 0),
                'human_score': pattern_result.get('human_score', 0),
                'analysis_summary': pattern_result.get('analysis', 'No pattern analysis available')
            }
        
        # Add neural analysis details if available
        if neural_available:
            result['neural_analysis'] = {
                'confidence': neural_result.get('confidence', 0),
                'available': True,
                'model': 'roberta-base-openai-detector'
            }
        
        return result
    
    def _generate_enhanced_feedback(self, ai_prob: float, confidence: float, 
                                  neural_result: Dict, pattern_result: Dict, text: str) -> Dict[str, List]:
        """
        Generate enhanced feedback including pattern analysis insights.
        
        Args:
            ai_prob (float): Combined AI probability
            confidence (float): Combined confidence
            neural_result (dict): Neural model results
            pattern_result (dict): Pattern detection results
            text (str): Original text
            
        Returns:
            dict: Enhanced feedback with pattern insights
        """
        messages = []
        flagged_sections = []
        recommendations = []
        
        # Add pattern-specific feedback
        if pattern_result.get('available', False):
            patterns = pattern_result.get('patterns_detected', [])
            
            # Group patterns by type
            ai_patterns = [p for p in patterns if p.get('type') == 'ai']
            human_patterns = [p for p in patterns if p.get('type') == 'human']
            
            if ai_patterns:
                ai_pattern_names = [p['description'] for p in ai_patterns[:3]]
                messages.append(f"AI writing patterns detected: {', '.join(ai_pattern_names)}")
                
                for pattern in ai_patterns[:2]:  # Top 2 AI patterns
                    flagged_sections.append({
                        'type': 'ai_pattern',
                        'description': pattern['description'],
                        'strength': pattern.get('strength', 0),
                        'impact': pattern.get('score_impact', 0)
                    })
            
            if human_patterns:
                human_pattern_names = [p['description'] for p in human_patterns[:3]]
                messages.append(f"Human writing patterns detected: {', '.join(human_pattern_names)}")
            
            # Add pattern-based recommendations
            if ai_patterns:
                recommendations.append("Consider reviewing for AI-typical language patterns and phrasing")
                if any('em-dash' in p['description'].lower() for p in ai_patterns):
                    recommendations.append("Excessive em-dash usage detected - consider varying punctuation")
                if any('qualifier' in p['description'].lower() for p in ai_patterns):
                    recommendations.append("High use of qualifying language - consider more direct statements")
        
        # Add neural model feedback
        if neural_result.get('available', False):
            neural_conf = neural_result.get('confidence', 0)
            if neural_conf > 0.8:
                messages.append("High neural model confidence in prediction")
            elif neural_conf < 0.4:
                messages.append("Lower neural model confidence - consider additional analysis")
        
        # Overall recommendations based on combined analysis
        if ai_prob > 0.7:
            recommendations.append("Text shows strong AI characteristics - verify authenticity")
        elif ai_prob < 0.3:
            recommendations.append("Text shows strong human characteristics")
        else:
            recommendations.append("Mixed signals detected - manual review recommended")
        
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
    
    def _calculate_pattern_strength(self, pattern_result: Dict) -> float:
        """
        Calculate the strength of detected patterns to determine dynamic weighting.
        
        Args:
            pattern_result (dict): Pattern detection results
            
        Returns:
            float: Pattern strength score (0.0 to 1.0)
        """
        if not pattern_result.get('available', False):
            return 0.0
        
        patterns_detected = pattern_result.get('patterns_detected', [])
        pattern_confidence = pattern_result.get('confidence', 0.5)
        ai_score = pattern_result.get('ai_score', 0.0)
        human_score = pattern_result.get('human_score', 0.0)
        
        # Base strength from number of patterns detected
        pattern_count_strength = min(len(patterns_detected) / 5.0, 1.0)  # Normalize to max 5 patterns
        
        # Strength from pattern confidence
        confidence_strength = pattern_confidence
        
        # Strength from score differential (how decisive the patterns are)
        score_differential = abs(ai_score - human_score)
        differential_strength = min(score_differential / 3.0, 1.0)  # Normalize to max difference of 3
        
        # Strong individual patterns that should have high influence
        strong_patterns = [
            'Excessive use of em-dashes',
            'AI-typical buzzwords and phrases',
            'Unnaturally uniform sentence lengths',
            'Corporate jargon and buzzwords'
        ]
        
        # Extra strong patterns that should dominate decisions
        extra_strong_patterns = [
            'Unnaturally uniform sentence lengths',
            'Excessive use of em-dashes'
        ]
        
        strong_pattern_count = sum(1 for pattern in patterns_detected 
                                 if any(strong in pattern for strong in strong_patterns))
        strong_pattern_strength = min(strong_pattern_count / 2.0, 1.0)  # Normalize to max 2 strong patterns
        
        # Extra boost for critical AI patterns
        extra_strong_count = sum(1 for pattern in patterns_detected 
                               if any(extra in pattern for extra in extra_strong_patterns))
        extra_strong_boost = min(extra_strong_count * 0.3, 0.6)  # Up to 60% boost for critical patterns
        
        # Combine all strength factors
        overall_strength = (
            pattern_count_strength * 0.2 +
            confidence_strength * 0.2 +
            differential_strength * 0.2 +
            strong_pattern_strength * 0.2 +
            extra_strong_boost * 0.2
        ) + extra_strong_boost
        
        return min(overall_strength, 1.0)
    
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