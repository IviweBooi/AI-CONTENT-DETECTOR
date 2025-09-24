#!/usr/bin/env python3
"""
Pattern-Based AI Detection Module

This module analyzes text for specific patterns and stylistic markers
that are commonly found in AI-generated content vs human-written content.
"""

import re
import string
from collections import Counter
from typing import Dict, List, Tuple, Any
import statistics

class PatternDetector:
    """
    Detects AI vs Human writing patterns based on stylistic analysis
    """
    
    def __init__(self):
        # AI-typical patterns (increase AI probability)
        self.ai_markers = {
            'excessive_em_dashes': {
                'pattern': r'—',
                'threshold': 3,  # More than 3 em-dashes in a text
                'weight': 0.15,
                'description': 'Excessive use of em-dashes'
            },
            'repetitive_sentence_starters': {
                'patterns': [
                    r'\b(Furthermore|Moreover|Additionally|In addition|However|Nevertheless|Nonetheless)\b',
                    r'\b(It is important to note|It should be noted|It is worth noting)\b',
                    r'\b(In conclusion|To conclude|In summary|To summarize)\b'
                ],
                'threshold': 0.3,  # 30% of sentences start with these
                'weight': 0.12,
                'description': 'Repetitive formal sentence starters'
            },
            'excessive_qualifiers': {
                'patterns': [
                    r'\b(potentially|possibly|likely|probably|generally|typically|usually|often|frequently)\b',
                    r'\b(somewhat|rather|quite|fairly|relatively|comparatively)\b',
                    r'\b(may|might|could|would|should)\b'
                ],
                'threshold': 0.15,  # More than 15% qualifier density
                'weight': 0.10,
                'description': 'Excessive use of qualifiers and hedging language'
            },
            'ai_cliches': {
                'patterns': [
                    r'\b(delve into|dive deep|unpack|leverage|utilize|optimize|streamline)\b',
                    r'\b(cutting-edge|state-of-the-art|revolutionary|groundbreaking|innovative)\b',
                    r'\b(comprehensive|holistic|robust|scalable|seamless|efficient)\b',
                    r'\b(it\'s worth noting|it\'s important to|it\'s crucial to)\b'
                ],
                'threshold': 2,  # More than 2 AI cliches
                'weight': 0.18,
                'description': 'AI-typical buzzwords and phrases'
            },
            'uniform_sentence_length': {
                'threshold': 0.8,  # Low variance in sentence length
                'weight': 0.08,
                'description': 'Unnaturally uniform sentence lengths'
            },
            'excessive_lists': {
                'patterns': [
                    r'(?:^|\n)\s*[\d\w]\.\s',  # Numbered lists
                    r'(?:^|\n)\s*[•\-\*]\s',   # Bullet points
                    r':\s*\n\s*[\d\w•\-\*]'   # Colon followed by list
                ],
                'threshold': 3,  # More than 3 list indicators
                'weight': 0.12,
                'description': 'Excessive use of lists and bullet points'
            }
        }
        
        # Human-typical patterns (decrease AI probability)
        self.human_markers = {
            'contractions': {
                'patterns': [
                    r"\b(don't|won't|can't|shouldn't|wouldn't|couldn't|isn't|aren't|wasn't|weren't)\b",
                    r"\b(I'm|you're|he's|she's|it's|we're|they're|I've|you've|we've|they've)\b",
                    r"\b(I'll|you'll|he'll|she'll|it'll|we'll|they'll|I'd|you'd|he'd|she'd|we'd|they'd)\b"
                ],
                'threshold': 2,  # At least 2 contractions
                'weight': -0.10,
                'description': 'Natural use of contractions'
            },
            'personal_pronouns': {
                'patterns': [r'\b(I|me|my|mine|myself)\b'],
                'threshold': 0.02,  # At least 2% personal pronoun density
                'weight': -0.08,
                'description': 'Personal voice and first-person perspective'
            },
            'informal_language': {
                'patterns': [
                    r'\b(yeah|yep|nope|okay|ok|alright|gonna|wanna|gotta)\b',
                    r'\b(pretty|really|very|super|totally|absolutely|definitely)\b',
                    r'\b(stuff|things|guys|folks|kinda|sorta)\b'
                ],
                'threshold': 1,  # At least 1 informal word
                'weight': -0.12,
                'description': 'Informal and conversational language'
            },
            'sentence_fragments': {
                'patterns': [
                    r'\b(And|But|Or|So|Because|Since|Although|Though|While)\s+[^.!?]*[.!?]',
                    r'^[A-Z][^.!?]*[.!?]$'  # Very short sentences
                ],
                'threshold': 1,  # At least 1 fragment
                'weight': -0.06,
                'description': 'Natural sentence fragments and varied structure'
            },
            'emotional_expressions': {
                'patterns': [
                    r'[!]{2,}|[?]{2,}',  # Multiple punctuation
                    r'\b(wow|amazing|awesome|terrible|horrible|fantastic|brilliant)\b',
                    r'\b(love|hate|adore|despise|enjoy|dislike)\b'
                ],
                'threshold': 1,  # At least 1 emotional expression
                'weight': -0.10,
                'description': 'Emotional language and expressions'
            },
            'varied_punctuation': {
                'threshold': 0.7,  # Good variety in punctuation usage
                'weight': -0.05,
                'description': 'Natural variation in punctuation'
            }
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for AI vs Human patterns
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict containing pattern analysis results
        """
        if not text or len(text.strip()) < 50:
            return {
                'ai_probability': 0.5,
                'confidence': 0.1,
                'patterns_detected': [],
                'analysis': 'Text too short for reliable pattern analysis'
            }
        
        # Prepare text for analysis
        sentences = self._split_sentences(text)
        words = text.split()
        
        ai_score = 0.0
        human_score = 0.0
        patterns_detected = []
        
        # Analyze AI markers
        for marker_name, marker_config in self.ai_markers.items():
            score, detected = self._analyze_marker(text, sentences, words, marker_config, marker_name, 'ai')
            ai_score += score
            if detected:
                patterns_detected.append(detected)
        
        # Analyze Human markers
        for marker_name, marker_config in self.human_markers.items():
            score, detected = self._analyze_marker(text, sentences, words, marker_config, marker_name, 'human')
            human_score += score  # Human markers have negative weights, so this decreases AI probability
            if detected:
                patterns_detected.append(detected)
        
        # Calculate final probability
        total_score = ai_score + human_score  # human_score is negative, so this reduces AI probability
        ai_probability = max(0.0, min(1.0, 0.5 + total_score))
        
        # Calculate confidence based on number of patterns detected
        confidence = min(0.9, 0.3 + (len(patterns_detected) * 0.1))
        
        return {
            'ai_probability': ai_probability,
            'human_probability': 1.0 - ai_probability,
            'confidence': confidence,
            'patterns_detected': patterns_detected,
            'ai_score': ai_score,
            'human_score': human_score,
            'total_patterns': len(patterns_detected),
            'analysis': self._generate_analysis_summary(patterns_detected, ai_probability)
        }
    
    def _analyze_marker(self, text: str, sentences: List[str], words: List[str], 
                       config: Dict, marker_name: str, marker_type: str) -> Tuple[float, Dict]:
        """Analyze a specific marker pattern"""
        
        if marker_name == 'uniform_sentence_length':
            return self._analyze_sentence_uniformity(sentences, config, marker_name)
        elif marker_name == 'varied_punctuation':
            return self._analyze_punctuation_variety(text, config, marker_name)
        else:
            return self._analyze_pattern_marker(text, sentences, words, config, marker_name, marker_type)
    
    def _analyze_pattern_marker(self, text: str, sentences: List[str], words: List[str],
                               config: Dict, marker_name: str, marker_type: str) -> Tuple[float, Dict]:
        """Analyze pattern-based markers"""
        
        if 'patterns' in config:
            # Multiple patterns
            total_matches = 0
            for pattern in config['patterns']:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                total_matches += matches
        else:
            # Single pattern
            pattern = config['pattern']
            total_matches = len(re.findall(pattern, text, re.IGNORECASE))
        
        # Calculate density or count based on marker type
        if marker_name in ['repetitive_sentence_starters', 'excessive_qualifiers', 'personal_pronouns']:
            density = total_matches / len(words) if words else 0
            triggered = density >= config['threshold']
            strength = min(1.0, density / config['threshold']) if triggered else 0
        else:
            triggered = total_matches >= config['threshold']
            strength = min(1.0, total_matches / config['threshold']) if triggered else 0
        
        score = config['weight'] * strength if triggered else 0
        
        detected = None
        if triggered:
            detected = {
                'type': marker_type,
                'name': marker_name,
                'description': config['description'],
                'count': total_matches,
                'strength': strength,
                'score_impact': score
            }
        
        return score, detected
    
    def _analyze_sentence_uniformity(self, sentences: List[str], config: Dict, marker_name: str) -> Tuple[float, Dict]:
        """Analyze sentence length uniformity"""
        if len(sentences) < 3:
            return 0, None
        
        lengths = [len(sentence.split()) for sentence in sentences]
        if not lengths:
            return 0, None
        
        # Calculate coefficient of variation (std/mean)
        mean_length = statistics.mean(lengths)
        if mean_length == 0:
            return 0, None
        
        std_length = statistics.stdev(lengths) if len(lengths) > 1 else 0
        cv = std_length / mean_length
        
        # Low coefficient of variation indicates uniformity
        uniformity = 1.0 - cv
        triggered = uniformity >= config['threshold']
        
        score = config['weight'] * uniformity if triggered else 0
        
        detected = None
        if triggered:
            detected = {
                'type': 'ai',
                'name': marker_name,
                'description': config['description'],
                'uniformity_score': uniformity,
                'avg_length': mean_length,
                'score_impact': score
            }
        
        return score, detected
    
    def _analyze_punctuation_variety(self, text: str, config: Dict, marker_name: str) -> Tuple[float, Dict]:
        """Analyze punctuation variety"""
        punctuation_chars = [char for char in text if char in string.punctuation]
        if not punctuation_chars:
            return 0, None
        
        unique_punct = len(set(punctuation_chars))
        total_punct = len(punctuation_chars)
        
        variety_score = unique_punct / total_punct if total_punct > 0 else 0
        triggered = variety_score >= config['threshold']
        
        score = config['weight'] * variety_score if triggered else 0
        
        detected = None
        if triggered:
            detected = {
                'type': 'human',
                'name': marker_name,
                'description': config['description'],
                'variety_score': variety_score,
                'unique_punctuation': unique_punct,
                'score_impact': score
            }
        
        return score, detected
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _generate_analysis_summary(self, patterns: List[Dict], ai_probability: float) -> str:
        """Generate a human-readable analysis summary"""
        if not patterns:
            return "No distinctive patterns detected"
        
        ai_patterns = [p for p in patterns if p['type'] == 'ai']
        human_patterns = [p for p in patterns if p['type'] == 'human']
        
        summary_parts = []
        
        if ai_patterns:
            ai_descriptions = [p['description'] for p in ai_patterns]
            summary_parts.append(f"AI indicators: {', '.join(ai_descriptions[:3])}")
        
        if human_patterns:
            human_descriptions = [p['description'] for p in human_patterns]
            summary_parts.append(f"Human indicators: {', '.join(human_descriptions[:3])}")
        
        if ai_probability > 0.7:
            summary_parts.append("Strong AI writing patterns detected")
        elif ai_probability < 0.3:
            summary_parts.append("Strong human writing patterns detected")
        else:
            summary_parts.append("Mixed writing patterns detected")
        
        return "; ".join(summary_parts)

# Example usage and testing
if __name__ == "__main__":
    detector = PatternDetector()
    
    # Test with AI-like text
    ai_text = """
    Furthermore, it is important to note that artificial intelligence has revolutionized numerous industries. Moreover, the cutting-edge technology continues to evolve at an unprecedented pace. Additionally, organizations must leverage these innovative solutions to optimize their operations and streamline their processes. In conclusion, the comprehensive implementation of AI systems will undoubtedly enhance efficiency and drive sustainable growth.
    """
    
    # Test with human-like text
    human_text = """
    I can't believe how much technology has changed our lives! It's pretty amazing when you think about it. My grandmother always says she never imagined we'd have computers in our pockets. But here we are, and honestly? I think we're just getting started. There's so much more to come, and I'm excited to see what happens next.
    """
    
    print("AI-like text analysis:")
    result = detector.analyze_text(ai_text)
    print(f"AI Probability: {result['ai_probability']:.3f}")
    print(f"Patterns: {len(result['patterns_detected'])}")
    print(f"Analysis: {result['analysis']}")
    print()
    
    print("Human-like text analysis:")
    result = detector.analyze_text(human_text)
    print(f"AI Probability: {result['ai_probability']:.3f}")
    print(f"Patterns: {len(result['patterns_detected'])}")
    print(f"Analysis: {result['analysis']}")