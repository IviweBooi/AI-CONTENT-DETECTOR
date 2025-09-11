#!/usr/bin/env python3
"""
Test script for confidence tuner functionality.
"""

from utils.confidence_tuner import ConfidenceTuner, ThresholdConfig

def test_confidence_tuner():
    """Test the confidence tuner with various scenarios."""
    print("Testing Confidence Tuner")
    print("=" * 40)
    
    tuner = ConfidenceTuner()
    
    # Test cases: (ai_prob, neural_conf, rule_conf, text_length)
    test_cases = [
        (0.85, 0.9, 0.8, 500, "High AI probability, good agreement"),
        (0.45, 0.6, 0.3, 100, "Borderline, poor agreement, short text"),
        (0.95, 0.95, 0.9, 1500, "Very high AI, excellent agreement, long text"),
        (0.15, 0.8, 0.2, 300, "Low AI, moderate agreement"),
        (0.0, 0.1, 0.18, 800, "Ensemble test case (from actual run)"),
    ]
    
    for i, (ai_prob, neural_conf, rule_conf, length, description) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {description}")
        print(f"Input: AI={ai_prob:.1%}, Neural={neural_conf:.1%}, Rule={rule_conf:.1%}, Length={length}")
        
        result = tuner.classify_with_confidence(ai_prob, neural_conf, rule_conf, length)
        
        print(f"Classification: {result['classification']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Indicators: {len(result['confidence_indicators'])} items")
        for indicator in result['confidence_indicators']:
            print(f"  - {indicator}")
        
        if result['threshold_info']['adjustments_applied']:
            print(f"Adjustments: {result['threshold_info']['adjustments_applied']}")
    
    print(f"\nPerformance Stats:")
    stats = tuner.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_confidence_tuner()