#!/usr/bin/env python3
"""
Test script for the pattern detector
"""

import sys
sys.path.append('.')
from utils.pattern_detector import PatternDetector

def test_pattern_detector():
    detector = PatternDetector()

    # Test AI-like text
    ai_text = """Furthermore, it is important to note that artificial intelligence has revolutionized numerous industries. Moreover, the cutting-edge technology continues to evolve at an unprecedented pace. Additionally, organizations must leverage these innovative solutions to optimize their operations and streamline their processes. In conclusion, the comprehensive implementation of AI systems will undoubtedly enhance efficiency and drive sustainable growth."""

    # Test human-like text
    human_text = """I can't believe how much technology has changed our lives! It's pretty amazing when you think about it. My grandmother always says she never imagined we'd have computers in our pockets. But here we are, and honestly? I think we're just getting started. There's so much more to come, and I'm excited to see what happens next."""

    print('=== AI-like text analysis ===')
    result = detector.analyze_text(ai_text)
    print(f'AI Probability: {result["ai_probability"]:.3f}')
    print(f'Patterns detected: {len(result["patterns_detected"])}')
    for pattern in result['patterns_detected']:
        print(f'  - {pattern["description"]} (strength: {pattern.get("strength", 0):.2f})')
    print(f'Analysis: {result["analysis"]}')
    print()

    print('=== Human-like text analysis ===')
    result = detector.analyze_text(human_text)
    print(f'AI Probability: {result["ai_probability"]:.3f}')
    print(f'Patterns detected: {len(result["patterns_detected"])}')
    for pattern in result['patterns_detected']:
        print(f'  - {pattern["description"]} (strength: {pattern.get("strength", 0):.2f})')
    print(f'Analysis: {result["analysis"]}')

if __name__ == "__main__":
    test_pattern_detector()