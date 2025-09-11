#!/usr/bin/env python3
"""
Test script for the ensemble AI detector to verify improved accuracy.
"""

import sys
import os

# Add parent directory to path to access utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.ensemble_detector import EnsembleAIDetector
    from utils.rule_based_detector import RuleBasedAIDetector
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the utils modules are available")
    # Don't exit during pytest execution
    import pytest
    pytest.skip(f"Skipping test due to import error: {e}", allow_module_level=True)

def test_ensemble_detector():
    """Test the ensemble detector with AI-generated sample text."""
    
    # Read the AI sample text
    sample_file = os.path.join(os.path.dirname(__file__), 'ai_sample_text.txt')
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_text = f.read().strip()
    except FileNotFoundError:
        print(f"Sample file not found: {sample_file}")
        return
    
    print("Testing Ensemble AI Detector")
    print("=" * 50)
    print(f"Text length: {len(sample_text)} characters")
    print(f"Sample text preview: {sample_text[:200]}...")
    print("=" * 50)
    
    # Test rule-based detector alone
    print("\n1. Rule-Based Detection Only:")
    print("-" * 30)
    rule_detector = RuleBasedAIDetector()
    rule_result = rule_detector.analyze_text(sample_text)
    
    print(f"AI Probability: {rule_result['ai_probability']:.1%}")
    print(f"Confidence: {rule_result['confidence']:.1%}")
    print(f"Flags: {len(rule_result['flags'])}")
    if rule_result['flags']:
        for flag in rule_result['flags'][:3]:
            print(f"  • {flag}")
    print(f"Reasoning: {rule_result['reasoning'][:2]}")
    
    # Test ensemble detector
    print("\n2. Ensemble Detection (Neural + Rule-Based):")
    print("-" * 45)
    ensemble_detector = EnsembleAIDetector()
    ensemble_result = ensemble_detector.detect(sample_text)
    
    print(f"AI Probability: {ensemble_result['ai_probability']:.1%}")
    print(f"Human Probability: {ensemble_result['human_probability']:.1%}")
    print(f"Confidence: {ensemble_result['confidence']:.1%}")
    print(f"Classification: {ensemble_result['classification']}")
    print(f"Risk Level: {ensemble_result['risk_level']}")
    
    if 'method_info' in ensemble_result:
        method_info = ensemble_result['method_info']
        print(f"Detection Method: {method_info.get('method', 'unknown')}")
        if 'neural_prediction' in method_info and method_info['neural_prediction'] is not None:
            print(f"Neural Prediction: {method_info['neural_prediction']:.1%}")
        if 'rule_prediction' in method_info and method_info['rule_prediction'] is not None:
            print(f"Rule Prediction: {method_info['rule_prediction']:.1%}")
        if 'agreement_score' in method_info:
            print(f"Agreement Score: {method_info['agreement_score']:.1%}")
    
    print("\nFeedback Messages:")
    for msg in ensemble_result.get('feedback_messages', [])[:5]:
        print(f"  • {msg}")
    
    if 'rule_based_analysis' in ensemble_result:
        print("\nRule-Based Analysis Details:")
        rule_analysis = ensemble_result['rule_based_analysis']
        if 'flags' in rule_analysis and rule_analysis['flags']:
            print(f"  Flags: {rule_analysis['flags'][:3]}")
        if 'reasoning' in rule_analysis and rule_analysis['reasoning']:
            print(f"  Reasoning: {rule_analysis['reasoning'][:2]}")
    
    print("\n" + "=" * 50)
    print("Comparison Summary:")
    print(f"Rule-Based Only:  {rule_result['ai_probability']:.1%} AI probability")
    print(f"Ensemble Method:  {ensemble_result['ai_probability']:.1%} AI probability")
    
    # Determine if ensemble is working better
    if ensemble_result['ai_probability'] > rule_result['ai_probability']:
        print("✅ Ensemble detector shows HIGHER AI probability (better for AI text)")
    elif ensemble_result['ai_probability'] < rule_result['ai_probability']:
        print("⚠️ Ensemble detector shows LOWER AI probability")
    else:
        print("➡️ Both methods show similar results")
    
    print(f"Ensemble confidence: {ensemble_result['confidence']:.1%}")
    
def test_ensemble_functionality():
    """Pytest test function for ensemble detector."""
    test_ensemble_detector()

if __name__ == "__main__":
    test_ensemble_detector()