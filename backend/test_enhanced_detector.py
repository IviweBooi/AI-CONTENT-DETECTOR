#!/usr/bin/env python3
"""
Test script for the enhanced ensemble detector with pattern analysis
"""

import sys
sys.path.append('.')
from utils.ensemble_detector import EnsembleAIDetector

def test_enhanced_detector():
    detector = EnsembleAIDetector()

    # Test AI-like text with typical AI patterns
    ai_text = """Furthermore, it is important to note that artificial intelligence has revolutionized numerous industries. Moreover, the cutting-edge technology continues to evolve at an unprecedented pace. Additionally, organizations must leverage these innovative solutions to optimize their operations and streamline their processes. In conclusion, the comprehensive implementation of AI systems will undoubtedly enhance efficiency and drive sustainable growth."""

    # Test human-like text with natural patterns
    human_text = """I can't believe how much technology has changed our lives! It's pretty amazing when you think about it. My grandmother always says she never imagined we'd have computers in our pockets. But here we are, and honestly? I think we're just getting started. There's so much more to come, and I'm excited to see what happens next."""

    # Test text with excessive em-dashes (AI pattern)
    em_dash_text = """The implementation of AI systems — particularly in healthcare — has shown remarkable results. These technologies — when properly deployed — can enhance diagnostic accuracy. Furthermore — and this is crucial — the integration must be seamless to ensure optimal outcomes."""

    print('=== AI-like text analysis ===')
    result = detector.detect(ai_text)
    print(f'AI Probability: {result["ai_probability"]:.3f}')
    print(f'Classification: {result["classification"]}')
    print(f'Method: {result["method_info"]["prediction_method"]}')
    if 'pattern_analysis' in result:
        print(f'Patterns detected: {result["pattern_analysis"]["total_patterns"]}')
        for pattern in result["pattern_analysis"]["patterns_detected"][:3]:
            print(f'  - {pattern["description"]}')
    print(f'Feedback: {result["feedback_messages"][:2]}')
    print()

    print('=== Human-like text analysis ===')
    result = detector.detect(human_text)
    print(f'AI Probability: {result["ai_probability"]:.3f}')
    print(f'Classification: {result["classification"]}')
    print(f'Method: {result["method_info"]["prediction_method"]}')
    if 'pattern_analysis' in result:
        print(f'Patterns detected: {result["pattern_analysis"]["total_patterns"]}')
        for pattern in result["pattern_analysis"]["patterns_detected"][:3]:
            print(f'  - {pattern["description"]}')
    print(f'Feedback: {result["feedback_messages"][:2]}')
    print()

    print('=== Em-dash text analysis ===')
    result = detector.detect(em_dash_text)
    print(f'AI Probability: {result["ai_probability"]:.3f}')
    print(f'Classification: {result["classification"]}')
    print(f'Method: {result["method_info"]["prediction_method"]}')
    if 'pattern_analysis' in result:
        print(f'Patterns detected: {result["pattern_analysis"]["total_patterns"]}')
        for pattern in result["pattern_analysis"]["patterns_detected"][:3]:
            print(f'  - {pattern["description"]}')
    print(f'Feedback: {result["feedback_messages"][:2]}')

if __name__ == "__main__":
    test_enhanced_detector()