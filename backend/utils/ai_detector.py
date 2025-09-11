import re
import string
from collections import Counter
import math

def detect_ai_content(text):
    """
    Detect AI-generated content using heuristic analysis
    
    This is a basic implementation that uses statistical and linguistic patterns
    to estimate the likelihood of AI-generated content. For production use,
    this should be replaced with trained ML models.
    
    Args:
        text (str): Text content to analyze
    
    Returns:
        dict: Analysis results with confidence scores
    """
    if not text or not text.strip():
        return {
            'error': 'Empty text provided',
            'ai_probability': 0,
            'confidence': 0,
            'analysis': {}
        }
    
    # Clean and prepare text
    cleaned_text = clean_text(text)
    
    # Perform various analyses
    analysis = {
        'word_count': len(cleaned_text.split()),
        'sentence_count': count_sentences(text),
        'avg_sentence_length': calculate_avg_sentence_length(text),
        'lexical_diversity': calculate_lexical_diversity(cleaned_text),
        'repetition_score': calculate_repetition_score(cleaned_text),
        'formality_score': calculate_formality_score(cleaned_text),
        'complexity_score': calculate_complexity_score(text),
        'pattern_score': detect_ai_patterns(text)
    }
    
    # Calculate AI probability based on heuristics
    ai_probability = calculate_ai_probability(analysis)
    confidence = calculate_confidence(analysis)
    
    # Determine classification
    if ai_probability >= 0.7:
        classification = 'AI-Generated'
        risk_level = 'High'
    elif ai_probability >= 0.4:
        classification = 'Possibly AI-Generated'
        risk_level = 'Medium'
    else:
        classification = 'Likely Human-Written'
        risk_level = 'Low'
    
    return {
        'ai_probability': round(ai_probability, 3),
        'human_probability': round(1 - ai_probability, 3),
        'confidence': round(confidence, 3),
        'classification': classification,
        'risk_level': risk_level,
        'analysis': analysis,
        'recommendations': generate_recommendations(analysis, ai_probability)
    }

def clean_text(text):
    """
    Clean text for analysis
    """
    # Remove extra whitespace and normalize
    text = ' '.join(text.split())
    # Remove URLs, emails, and special characters for word analysis
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    return text

def count_sentences(text):
    """
    Count sentences in text
    """
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def calculate_avg_sentence_length(text):
    """
    Calculate average sentence length
    """
    sentences = re.split(r'[.!?]+', text)
    valid_sentences = [s.strip() for s in sentences if s.strip()]
    
    if not valid_sentences:
        return 0
    
    total_words = sum(len(s.split()) for s in valid_sentences)
    return total_words / len(valid_sentences)

def calculate_lexical_diversity(text):
    """
    Calculate lexical diversity (unique words / total words)
    """
    words = text.lower().split()
    if not words:
        return 0
    
    unique_words = set(words)
    return len(unique_words) / len(words)

def calculate_repetition_score(text):
    """
    Calculate repetition score based on repeated phrases
    """
    words = text.lower().split()
    if len(words) < 4:
        return 0
    
    # Check for repeated 3-word phrases
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
    trigram_counts = Counter(trigrams)
    
    repeated_trigrams = sum(count - 1 for count in trigram_counts.values() if count > 1)
    return repeated_trigrams / len(trigrams) if trigrams else 0

def calculate_formality_score(text):
    """
    Calculate formality score based on word choices
    """
    words = text.lower().split()
    if not words:
        return 0
    
    # Formal indicators
    formal_words = {'however', 'therefore', 'furthermore', 'moreover', 'consequently', 
                   'nevertheless', 'accordingly', 'subsequently', 'additionally'}
    
    # Informal indicators
    informal_words = {'really', 'pretty', 'quite', 'very', 'super', 'totally', 
                     'basically', 'literally', 'actually', 'definitely'}
    
    formal_count = sum(1 for word in words if word in formal_words)
    informal_count = sum(1 for word in words if word in informal_words)
    
    if formal_count + informal_count == 0:
        return 0.5
    
    return formal_count / (formal_count + informal_count)

def calculate_complexity_score(text):
    """
    Calculate text complexity based on sentence structure
    """
    sentences = re.split(r'[.!?]+', text)
    valid_sentences = [s.strip() for s in sentences if s.strip()]
    
    if not valid_sentences:
        return 0
    
    complexity_indicators = 0
    total_sentences = len(valid_sentences)
    
    for sentence in valid_sentences:
        # Count subordinate clauses
        subordinate_words = ['because', 'although', 'while', 'since', 'whereas', 
                           'if', 'unless', 'when', 'where', 'who', 'which', 'that']
        complexity_indicators += sum(1 for word in subordinate_words if word in sentence.lower())
    
    return complexity_indicators / total_sentences if total_sentences > 0 else 0

def detect_ai_patterns(text):
    """
    Detect patterns commonly found in AI-generated text
    """
    ai_patterns = [
        r'\bin conclusion\b',
        r'\bit is important to note\b',
        r'\bit should be noted\b',
        r'\boverall\b.*\b(positive|negative|good|bad)\b',
        r'\bfurthermore\b.*\bhowever\b',
        r'\bon the other hand\b',
        r'\bin summary\b',
        r'\bto summarize\b'
    ]
    
    pattern_count = 0
    for pattern in ai_patterns:
        if re.search(pattern, text.lower()):
            pattern_count += 1
    
    return pattern_count / len(ai_patterns)

def calculate_ai_probability(analysis):
    """
    Calculate AI probability based on analysis metrics
    """
    # Weights for different factors
    weights = {
        'avg_sentence_length': 0.15,
        'lexical_diversity': 0.20,
        'repetition_score': 0.15,
        'formality_score': 0.15,
        'complexity_score': 0.15,
        'pattern_score': 0.20
    }
    
    # Normalize and score each factor
    scores = {}
    
    # Average sentence length (AI tends to be more consistent)
    avg_len = analysis['avg_sentence_length']
    if 15 <= avg_len <= 25:  # AI sweet spot
        scores['avg_sentence_length'] = 0.7
    elif 10 <= avg_len <= 30:
        scores['avg_sentence_length'] = 0.4
    else:
        scores['avg_sentence_length'] = 0.2
    
    # Lexical diversity (AI tends to be lower)
    diversity = analysis['lexical_diversity']
    if diversity < 0.4:
        scores['lexical_diversity'] = 0.8
    elif diversity < 0.6:
        scores['lexical_diversity'] = 0.5
    else:
        scores['lexical_diversity'] = 0.2
    
    # Repetition score (higher = more AI-like)
    scores['repetition_score'] = min(analysis['repetition_score'] * 2, 1.0)
    
    # Formality score (AI tends to be more formal)
    formality = analysis['formality_score']
    if formality > 0.7:
        scores['formality_score'] = 0.7
    elif formality > 0.3:
        scores['formality_score'] = 0.4
    else:
        scores['formality_score'] = 0.3
    
    # Complexity score (AI tends to be moderate)
    complexity = analysis['complexity_score']
    if 0.3 <= complexity <= 0.7:
        scores['complexity_score'] = 0.6
    else:
        scores['complexity_score'] = 0.3
    
    # Pattern score (direct indicator)
    scores['pattern_score'] = analysis['pattern_score']
    
    # Calculate weighted average
    ai_probability = sum(scores[factor] * weights[factor] for factor in weights)
    
    return min(max(ai_probability, 0), 1)  # Clamp between 0 and 1

def calculate_confidence(analysis):
    """
    Calculate confidence in the prediction
    """
    word_count = analysis['word_count']
    
    # Base confidence on text length
    if word_count < 50:
        base_confidence = 0.3
    elif word_count < 200:
        base_confidence = 0.6
    elif word_count < 500:
        base_confidence = 0.8
    else:
        base_confidence = 0.9
    
    # Adjust based on analysis consistency
    pattern_strength = analysis['pattern_score']
    repetition_strength = analysis['repetition_score']
    
    consistency_bonus = (pattern_strength + repetition_strength) * 0.1
    
    return min(base_confidence + consistency_bonus, 1.0)

def generate_recommendations(analysis, ai_probability):
    """
    Generate recommendations based on analysis
    """
    recommendations = []
    
    if ai_probability >= 0.7:
        recommendations.append("High likelihood of AI generation detected")
        recommendations.append("Consider manual review for verification")
    elif ai_probability >= 0.4:
        recommendations.append("Moderate AI indicators present")
        recommendations.append("Additional analysis may be needed")
    else:
        recommendations.append("Low AI indicators detected")
        recommendations.append("Text appears to be human-written")
    
    # Specific recommendations based on metrics
    if analysis['repetition_score'] > 0.3:
        recommendations.append("High repetition detected - common in AI text")
    
    if analysis['pattern_score'] > 0.3:
        recommendations.append("AI-typical phrases detected")
    
    if analysis['lexical_diversity'] < 0.4:
        recommendations.append("Low vocabulary diversity - potential AI indicator")
    
    return recommendations