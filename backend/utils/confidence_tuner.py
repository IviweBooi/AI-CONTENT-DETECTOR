#!/usr/bin/env python3
"""
Confidence Threshold Tuning and Classification Logic Improvements

This module provides dynamic threshold adjustment and improved classification logic
for better AI detection accuracy.
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ThresholdConfig:
    """Configuration for threshold tuning."""
    ai_threshold: float = 0.5
    confidence_threshold: float = 0.7
    high_confidence_threshold: float = 0.9
    low_confidence_threshold: float = 0.3
    
    # Risk level thresholds
    very_high_risk: float = 0.9
    high_risk: float = 0.7
    medium_risk: float = 0.5
    low_risk: float = 0.3

class ConfidenceTuner:
    """
    Dynamic confidence threshold tuning for AI detection.
    """
    
    def __init__(self, config: Optional[ThresholdConfig] = None):
        self.config = config or ThresholdConfig()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.prediction_history = []
        self.accuracy_metrics = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'high_confidence_correct': 0,
            'high_confidence_total': 0
        }
    
    def classify_with_confidence(self, ai_probability: float, 
                               neural_confidence: float = None,
                               rule_confidence: float = None,
                               text_length: int = None) -> Dict[str, Any]:
        """
        Classify text with dynamic confidence adjustment.
        
        Args:
            ai_probability: AI probability from model
            neural_confidence: Confidence from neural model
            rule_confidence: Confidence from rule-based model
            text_length: Length of analyzed text
            
        Returns:
            dict: Enhanced classification results
        """
        # Adjust thresholds based on text characteristics
        adjusted_config = self._adjust_thresholds(
            ai_probability, neural_confidence, rule_confidence, text_length
        )
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            ai_probability, neural_confidence, rule_confidence
        )
        
        # Determine classification
        classification = self._determine_classification(
            ai_probability, overall_confidence, adjusted_config
        )
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(
            ai_probability, overall_confidence, adjusted_config
        )
        
        # Generate confidence indicators
        confidence_indicators = self._generate_confidence_indicators(
            ai_probability, overall_confidence, adjusted_config
        )
        
        result = {
            'ai_probability': ai_probability,
            'human_probability': 1.0 - ai_probability,
            'confidence': overall_confidence,
            'classification': classification,
            'risk_level': risk_level,
            'confidence_indicators': confidence_indicators,
            'threshold_info': {
                'ai_threshold': adjusted_config.ai_threshold,
                'confidence_threshold': adjusted_config.confidence_threshold,
                'adjustments_applied': self._get_adjustment_reasons(
                    ai_probability, neural_confidence, rule_confidence, text_length
                )
            }
        }
        
        # Track prediction for performance monitoring
        self._track_prediction(result)
        
        return result
    
    def _adjust_thresholds(self, ai_probability: float,
                          neural_confidence: float,
                          rule_confidence: float,
                          text_length: int) -> ThresholdConfig:
        """
        Dynamically adjust thresholds based on input characteristics.
        """
        adjusted = ThresholdConfig(
            ai_threshold=self.config.ai_threshold,
            confidence_threshold=self.config.confidence_threshold,
            high_confidence_threshold=self.config.high_confidence_threshold,
            low_confidence_threshold=self.config.low_confidence_threshold,
            very_high_risk=self.config.very_high_risk,
            high_risk=self.config.high_risk,
            medium_risk=self.config.medium_risk,
            low_risk=self.config.low_risk
        )
        
        # Adjust based on text length
        if text_length:
            if text_length < 100:  # Short text - be more conservative
                adjusted.ai_threshold += 0.1
                adjusted.confidence_threshold += 0.1
            elif text_length > 1000:  # Long text - can be more confident
                adjusted.ai_threshold -= 0.05
                adjusted.confidence_threshold -= 0.05
        
        # Adjust based on model agreement
        if neural_confidence and rule_confidence:
            agreement = 1.0 - abs(neural_confidence - rule_confidence)
            if agreement > 0.8:  # High agreement - lower thresholds
                adjusted.confidence_threshold -= 0.1
            elif agreement < 0.4:  # Low agreement - raise thresholds
                adjusted.confidence_threshold += 0.15
        
        # Adjust based on extreme probabilities
        if ai_probability > 0.9 or ai_probability < 0.1:
            adjusted.confidence_threshold -= 0.1  # More confident with extreme values
        
        # Ensure thresholds stay within reasonable bounds
        adjusted.ai_threshold = max(0.1, min(0.9, adjusted.ai_threshold))
        adjusted.confidence_threshold = max(0.3, min(0.95, adjusted.confidence_threshold))
        
        return adjusted
    
    def _calculate_overall_confidence(self, ai_probability: float,
                                    neural_confidence: float,
                                    rule_confidence: float) -> float:
        """
        Calculate overall confidence from multiple sources.
        """
        confidences = []
        
        # Base confidence from probability extremeness
        prob_confidence = 2 * abs(ai_probability - 0.5)  # 0 at 0.5, 1 at 0/1
        confidences.append(prob_confidence)
        
        # Add neural confidence if available
        if neural_confidence is not None:
            confidences.append(neural_confidence)
        
        # Add rule confidence if available
        if rule_confidence is not None:
            confidences.append(rule_confidence)
        
        # Calculate weighted average (give more weight to model confidences)
        if len(confidences) == 1:
            return confidences[0]
        elif len(confidences) == 2:
            return 0.3 * confidences[0] + 0.7 * confidences[1]
        else:  # All three available
            return 0.2 * confidences[0] + 0.4 * confidences[1] + 0.4 * confidences[2]
    
    def _determine_classification(self, ai_probability: float,
                                confidence: float,
                                config: ThresholdConfig) -> str:
        """
        Determine classification based on probability and confidence.
        """
        if confidence < config.low_confidence_threshold:
            return "Uncertain - Low Confidence"
        
        if ai_probability >= config.ai_threshold:
            if confidence >= config.high_confidence_threshold:
                return "Highly Likely AI-Generated"
            elif confidence >= config.confidence_threshold:
                return "Likely AI-Generated"
            else:
                return "Possibly AI-Generated"
        else:
            if confidence >= config.high_confidence_threshold:
                return "Highly Likely Human-Written"
            elif confidence >= config.confidence_threshold:
                return "Likely Human-Written"
            else:
                return "Possibly Human-Written"
    
    def _calculate_risk_level(self, ai_probability: float,
                            confidence: float,
                            config: ThresholdConfig) -> str:
        """
        Calculate risk level for AI content.
        """
        if ai_probability >= config.very_high_risk and confidence >= config.high_confidence_threshold:
            return "Very High"
        elif ai_probability >= config.high_risk and confidence >= config.confidence_threshold:
            return "High"
        elif ai_probability >= config.medium_risk:
            return "Medium"
        elif ai_probability >= config.low_risk:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_confidence_indicators(self, ai_probability: float,
                                      confidence: float,
                                      config: ThresholdConfig) -> List[str]:
        """
        Generate human-readable confidence indicators.
        """
        indicators = []
        
        # Confidence level indicators
        if confidence >= config.high_confidence_threshold:
            indicators.append("🎯 High confidence in detection results")
        elif confidence >= config.confidence_threshold:
            indicators.append("✅ Moderate confidence in detection results")
        else:
            indicators.append("⚠️ Low confidence - results may be uncertain")
        
        # Probability indicators
        if ai_probability > 0.9:
            indicators.append("🤖 Very strong AI indicators detected")
        elif ai_probability > 0.7:
            indicators.append("🔍 Strong AI patterns identified")
        elif ai_probability > 0.5:
            indicators.append("📊 Some AI characteristics present")
        elif ai_probability > 0.3:
            indicators.append("👤 Mostly human-like characteristics")
        else:
            indicators.append("✨ Strong human writing indicators")
        
        # Additional context
        if confidence < config.low_confidence_threshold:
            indicators.append("💡 Consider additional analysis methods")
        
        return indicators
    
    def _get_adjustment_reasons(self, ai_probability: float,
                              neural_confidence: float,
                              rule_confidence: float,
                              text_length: int) -> List[str]:
        """
        Get reasons for threshold adjustments.
        """
        reasons = []
        
        if text_length:
            if text_length < 100:
                reasons.append("Increased thresholds for short text")
            elif text_length > 1000:
                reasons.append("Decreased thresholds for long text")
        
        if neural_confidence and rule_confidence:
            agreement = 1.0 - abs(neural_confidence - rule_confidence)
            if agreement > 0.8:
                reasons.append("Decreased thresholds due to high model agreement")
            elif agreement < 0.4:
                reasons.append("Increased thresholds due to low model agreement")
        
        if ai_probability > 0.9 or ai_probability < 0.1:
            reasons.append("Adjusted for extreme probability values")
        
        return reasons
    
    def _track_prediction(self, result: Dict[str, Any]):
        """
        Track prediction for performance monitoring.
        """
        self.prediction_history.append({
            'ai_probability': result['ai_probability'],
            'confidence': result['confidence'],
            'classification': result['classification'],
            'risk_level': result['risk_level']
        })
        
        # Keep only last 1000 predictions
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-1000:]
        
        self.accuracy_metrics['total_predictions'] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        """
        if not self.prediction_history:
            return {'message': 'No predictions tracked yet'}
        
        recent_predictions = self.prediction_history[-100:]  # Last 100
        
        avg_confidence = np.mean([p['confidence'] for p in recent_predictions])
        avg_ai_prob = np.mean([p['ai_probability'] for p in recent_predictions])
        
        classification_counts = {}
        for pred in recent_predictions:
            cls = pred['classification']
            classification_counts[cls] = classification_counts.get(cls, 0) + 1
        
        return {
            'total_predictions': len(self.prediction_history),
            'recent_predictions': len(recent_predictions),
            'average_confidence': avg_confidence,
            'average_ai_probability': avg_ai_prob,
            'classification_distribution': classification_counts,
            'current_thresholds': {
                'ai_threshold': self.config.ai_threshold,
                'confidence_threshold': self.config.confidence_threshold
            }
        }
    
    def update_thresholds(self, new_config: ThresholdConfig):
        """
        Update threshold configuration.
        """
        self.config = new_config
        self.logger.info(f"Updated thresholds: {new_config}")


def create_tuned_classifier(ai_probability: float,
                          neural_confidence: float = None,
                          rule_confidence: float = None,
                          text_length: int = None,
                          custom_config: ThresholdConfig = None) -> Dict[str, Any]:
    """
    Convenience function for tuned classification.
    
    Args:
        ai_probability: AI probability from detection model
        neural_confidence: Confidence from neural model
        rule_confidence: Confidence from rule-based model
        text_length: Length of analyzed text
        custom_config: Custom threshold configuration
        
    Returns:
        dict: Enhanced classification results
    """
    tuner = ConfidenceTuner(custom_config)
    return tuner.classify_with_confidence(
        ai_probability, neural_confidence, rule_confidence, text_length
    )


if __name__ == "__main__":
    # Example usage
    tuner = ConfidenceTuner()
    
    # Test with different scenarios
    test_cases = [
        (0.85, 0.9, 0.8, 500),  # High AI probability, good agreement
        (0.45, 0.6, 0.3, 100),  # Borderline, poor agreement, short text
        (0.95, 0.95, 0.9, 1500), # Very high AI, excellent agreement, long text
        (0.15, 0.8, 0.2, 300),  # Low AI, moderate agreement
    ]
    
    print("Confidence Tuning Test Results")
    print("=" * 50)
    
    for i, (ai_prob, neural_conf, rule_conf, length) in enumerate(test_cases, 1):
        result = tuner.classify_with_confidence(ai_prob, neural_conf, rule_conf, length)
        
        print(f"\nTest Case {i}:")
        print(f"  Input: AI={ai_prob:.1%}, Neural={neural_conf:.1%}, Rule={rule_conf:.1%}, Length={length}")
        print(f"  Classification: {result['classification']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Adjustments: {result['threshold_info']['adjustments_applied']}")
    
    print(f"\nPerformance Stats: {tuner.get_performance_stats()}")