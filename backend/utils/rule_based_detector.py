import re
import string
from typing import Dict, List, Tuple, Union
from collections import Counter
import math

class RuleBasedAIDetector:
    """
    Rule-based AI content detection using linguistic patterns and statistical analysis.
    This provides immediate accuracy improvements and can work as a fallback when our main model fails.
    """
    
    def __init__(self):
        # Common AI-generated text patterns
        self.ai_phrases = {
            'formal_transitions': [
                'furthermore', 'moreover', 'additionally', 'consequently', 'nevertheless',
                'nonetheless', 'therefore', 'thus', 'hence', 'accordingly', 'subsequently',
                'in conclusion', 'to summarize', 'in summary', 'to conclude', 'overall',
                'in essence', 'fundamentally', 'essentially', 'ultimately', 'notably'
            ],
            'hedging_language': [
                'it is important to note', 'it should be noted', 'it is worth noting',
                'it is crucial to understand', 'it is essential to', 'it is vital to',
                'one must consider', 'it is imperative', 'it is paramount'
            ],
            'generic_statements': [
                'in today\'s world', 'in our modern society', 'in the digital age',
                'in recent years', 'with the advancement of', 'as technology evolves',
                'in the 21st century', 'in contemporary times', 'in this day and age'
            ],
            'ai_buzzwords': [
                'paradigm shift', 'cutting-edge', 'state-of-the-art', 'revolutionary',
                'groundbreaking', 'innovative solutions', 'synergistic', 'holistic approach',
                'comprehensive framework', 'multifaceted', 'unprecedented', 'transformative',
                'game-changing', 'next-generation', 'seamless integration', 'robust solution'
            ],
            'repetitive_structures': [
                'not only.*but also', 'on one hand.*on the other hand',
                'first.*second.*third', 'firstly.*secondly.*thirdly'
            ]
        }
        
        # Human-like indicators
        self.human_indicators = {
            'contractions': ["don't", "won't", "can't", "isn't", "aren't", "wasn't", "weren't", 
                           "haven't", "hasn't", "hadn't", "wouldn't", "couldn't", "shouldn't"],
            'informal_language': ["yeah", "nah", "gonna", "wanna", "gotta", "kinda", "sorta", 
                                "pretty much", "you know", "i mean", "like", "totally"],
            'personal_pronouns': ["i", "me", "my", "myself", "we", "us", "our", "ourselves"],
            'emotional_expressions': ["!", "!!", "!!!", "???", "omg", "wow", "lol", "haha", 
                                    "awesome", "terrible", "amazing", "horrible"]
        }
    
    def analyze_text(self, text: str) -> Dict[str, Union[float, Dict, List]]:
        """
        Perform comprehensive rule-based analysis of text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Analysis results with AI probability and detailed metrics
        """
        if not text or len(text.strip()) < 10:
            return {
                'ai_probability': 0.0,
                'confidence': 0.1,
                'features': {},
                'flags': [],
                'reasoning': ['Text too short for reliable analysis']
            }
        
        # Normalize text for analysis
        text_lower = text.lower()
        sentences = self._split_sentences(text)
        words = text_lower.split()
        
        # Calculate various features
        features = {
            'length_metrics': self._analyze_length_patterns(text, sentences, words),
            'vocabulary_metrics': self._analyze_vocabulary(words, text_lower),
            'structure_metrics': self._analyze_structure(sentences, text),
            'pattern_metrics': self._analyze_ai_patterns(text_lower),
            'human_indicators': self._analyze_human_indicators(text_lower),
            'statistical_metrics': self._analyze_statistical_patterns(words, sentences)
        }
        
        # Calculate AI probability based on features
        ai_probability, confidence, flags, reasoning = self._calculate_ai_probability(features)
        
        return {
            'ai_probability': round(ai_probability, 3),
            'confidence': round(confidence, 3),
            'features': features,
            'flags': flags,
            'reasoning': reasoning
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using multiple delimiters."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_length_patterns(self, text: str, sentences: List[str], words: List[str]) -> Dict[str, float]:
        """Analyze length-based patterns that may indicate AI generation."""
        if not sentences or not words:
            return {'avg_sentence_length': 0, 'sentence_length_variance': 0, 'avg_word_length': 0}
        
        sentence_lengths = [len(s.split()) for s in sentences]
        word_lengths = [len(word.strip(string.punctuation)) for word in words]
        
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        sentence_variance = sum((x - avg_sentence_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        avg_word_length = sum(word_lengths) / len(word_lengths)
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'sentence_length_variance': sentence_variance,
            'avg_word_length': avg_word_length,
            'total_sentences': len(sentences),
            'total_words': len(words)
        }
    
    def _analyze_vocabulary(self, words: List[str], text_lower: str) -> Dict[str, float]:
        """Analyze vocabulary complexity and diversity."""
        if not words:
            return {'vocabulary_diversity': 0, 'complex_word_ratio': 0, 'repetition_score': 0}
        
        # Vocabulary diversity (unique words / total words)
        unique_words = set(word.strip(string.punctuation) for word in words)
        vocabulary_diversity = len(unique_words) / len(words)
        
        # Complex word ratio (words > 6 characters)
        complex_words = [w for w in words if len(w.strip(string.punctuation)) > 6]
        complex_word_ratio = len(complex_words) / len(words)
        
        # Repetition analysis
        word_counts = Counter(word.strip(string.punctuation) for word in words)
        repetition_score = sum(count for count in word_counts.values() if count > 1) / len(words)
        
        return {
            'vocabulary_diversity': vocabulary_diversity,
            'complex_word_ratio': complex_word_ratio,
            'repetition_score': repetition_score,
            'unique_word_count': len(unique_words)
        }
    
    def _analyze_structure(self, sentences: List[str], text: str) -> Dict[str, float]:
        """Analyze structural patterns in the text."""
        if not sentences:
            return {'punctuation_density': 0, 'capitalization_score': 0, 'paragraph_structure': 0}
        
        # Punctuation analysis
        punctuation_count = sum(1 for char in text if char in string.punctuation)
        punctuation_density = punctuation_count / len(text) if text else 0
        
        # Capitalization patterns
        capital_count = sum(1 for char in text if char.isupper())
        capitalization_score = capital_count / len(text) if text else 0
        
        # Paragraph structure (line breaks)
        paragraphs = text.split('\n\n')
        paragraph_structure = len(paragraphs) / len(sentences) if sentences else 0
        
        return {
            'punctuation_density': punctuation_density,
            'capitalization_score': capitalization_score,
            'paragraph_structure': paragraph_structure,
            'paragraph_count': len(paragraphs)
        }
    
    def _analyze_ai_patterns(self, text_lower: str) -> Dict[str, Union[float, List]]:
        """Detect patterns commonly found in AI-generated text."""
        pattern_scores = {}
        detected_patterns = []
        
        for category, phrases in self.ai_phrases.items():
            matches = []
            for phrase in phrases:
                if phrase in text_lower:
                    matches.append(phrase)
            
            pattern_scores[category] = len(matches)
            if matches:
                detected_patterns.extend([(category, phrase) for phrase in matches])
        
        # Check for repetitive structures using regex
        for regex_pattern in self.ai_phrases['repetitive_structures']:
            if re.search(regex_pattern, text_lower):
                pattern_scores['repetitive_structures'] = pattern_scores.get('repetitive_structures', 0) + 1
                detected_patterns.append(('repetitive_structures', regex_pattern))
        
        total_ai_patterns = sum(pattern_scores.values())
        
        return {
            'total_ai_patterns': total_ai_patterns,
            'pattern_breakdown': pattern_scores,
            'detected_patterns': detected_patterns,
            'pattern_density': total_ai_patterns / len(text_lower.split()) if text_lower.split() else 0
        }
    
    def _analyze_human_indicators(self, text_lower: str) -> Dict[str, Union[float, List]]:
        """Detect patterns commonly found in human-written text."""
        human_scores = {}
        detected_indicators = []
        
        for category, indicators in self.human_indicators.items():
            matches = []
            for indicator in indicators:
                if indicator in text_lower:
                    matches.append(indicator)
            
            human_scores[category] = len(matches)
            if matches:
                detected_indicators.extend([(category, indicator) for indicator in matches])
        
        total_human_indicators = sum(human_scores.values())
        
        return {
            'total_human_indicators': total_human_indicators,
            'indicator_breakdown': human_scores,
            'detected_indicators': detected_indicators,
            'indicator_density': total_human_indicators / len(text_lower.split()) if text_lower.split() else 0
        }
    
    def _analyze_statistical_patterns(self, words: List[str], sentences: List[str]) -> Dict[str, float]:
        """Analyze statistical patterns that may indicate AI generation."""
        if not words or not sentences:
            return {'entropy': 0, 'burstiness': 0, 'coherence_score': 0}
        
        # Calculate text entropy (measure of randomness)
        word_freq = Counter(words)
        total_words = len(words)
        entropy = -sum((freq/total_words) * math.log2(freq/total_words) for freq in word_freq.values())
        
        # Burstiness (variation in word usage)
        word_positions = {}
        for i, word in enumerate(words):
            if word not in word_positions:
                word_positions[word] = []
            word_positions[word].append(i)
        
        # Calculate average gap between repeated words
        gaps = []
        for positions in word_positions.values():
            if len(positions) > 1:
                for i in range(1, len(positions)):
                    gaps.append(positions[i] - positions[i-1])
        
        burstiness = sum(gaps) / len(gaps) if gaps else 0
        
        # Simple coherence score based on sentence length consistency
        sentence_lengths = [len(s.split()) for s in sentences]
        if len(sentence_lengths) > 1:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            coherence_score = 1 - (sum(abs(length - avg_length) for length in sentence_lengths) / 
                                 (len(sentence_lengths) * avg_length))
        else:
            coherence_score = 1.0
        
        return {
            'entropy': entropy,
            'burstiness': burstiness,
            'coherence_score': max(0, coherence_score)
        }
    
    def _calculate_ai_probability(self, features: Dict) -> Tuple[float, float, List[str], List[str]]:
        """Calculate AI probability based on extracted features."""
        ai_score = 0.0
        confidence = 0.0
        flags = []
        reasoning = []
        
        # Weight different feature categories
        weights = {
            'ai_patterns': 0.3,
            'human_indicators': -0.25,
            'length_patterns': 0.15,
            'vocabulary': 0.15,
            'structure': 0.1,
            'statistical': 0.05
        }
        
        # AI pattern analysis
        pattern_metrics = features['pattern_metrics']
        if pattern_metrics['total_ai_patterns'] > 0:
            pattern_score = min(pattern_metrics['pattern_density'] * 10, 1.0)
            ai_score += weights['ai_patterns'] * pattern_score
            flags.append(f"AI patterns detected: {pattern_metrics['total_ai_patterns']}")
            reasoning.append(f"Found {pattern_metrics['total_ai_patterns']} AI-typical phrases")
        
        # Human indicator analysis
        human_metrics = features['human_indicators']
        if human_metrics['total_human_indicators'] > 0:
            human_score = min(human_metrics['indicator_density'] * 10, 1.0)
            ai_score += weights['human_indicators'] * human_score
            reasoning.append(f"Found {human_metrics['total_human_indicators']} human-like indicators")
        
        # Length pattern analysis
        length_metrics = features['length_metrics']
        if length_metrics['avg_sentence_length'] > 25:
            ai_score += weights['length_patterns'] * 0.5
            flags.append("Unusually long sentences detected")
            reasoning.append("Average sentence length suggests AI generation")
        
        if length_metrics['sentence_length_variance'] < 10:
            ai_score += weights['length_patterns'] * 0.3
            flags.append("Low sentence length variation")
            reasoning.append("Consistent sentence lengths may indicate AI")
        
        # Vocabulary analysis
        vocab_metrics = features['vocabulary_metrics']
        if vocab_metrics['complex_word_ratio'] > 0.3:
            ai_score += weights['vocabulary'] * 0.4
            flags.append("High complex word usage")
            reasoning.append("High proportion of complex words")
        
        if vocab_metrics['vocabulary_diversity'] < 0.6:
            ai_score += weights['vocabulary'] * 0.3
            flags.append("Low vocabulary diversity")
            reasoning.append("Limited vocabulary diversity detected")
        
        # Structure analysis
        structure_metrics = features['structure_metrics']
        if structure_metrics['punctuation_density'] > 0.1:
            ai_score += weights['structure'] * 0.3
            reasoning.append("High punctuation density")
        
        # Statistical analysis
        stat_metrics = features['statistical_metrics']
        if stat_metrics['coherence_score'] > 0.9:
            ai_score += weights['statistical'] * 0.5
            flags.append("Very high coherence score")
            reasoning.append("Unusually consistent text structure")
        
        # Normalize AI score to probability
        ai_probability = max(0.0, min(1.0, ai_score))
        
        # Calculate confidence based on feature strength
        feature_count = sum(1 for category in features.values() 
                          if isinstance(category, dict) and any(v > 0 for v in category.values() if isinstance(v, (int, float))))
        confidence = min(0.9, 0.3 + (feature_count * 0.1))
        
        if not reasoning:
            reasoning.append("No strong indicators detected")
        
        return ai_probability, confidence, flags, reasoning

# Convenience function for easy integration
def detect_ai_patterns(text: str) -> Dict[str, Union[float, Dict, List]]:
    """
    Quick function to detect AI patterns in text using rule-based analysis.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Analysis results
    """
    detector = RuleBasedAIDetector()
    return detector.analyze_text(text)