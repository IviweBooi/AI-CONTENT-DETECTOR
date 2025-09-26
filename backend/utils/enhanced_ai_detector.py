import os
import sys
from typing import Dict, List, Union

# Add predictor_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor_model'))

try:
    from predictor_model.ai_text_classifier import AITextClassifier
    MODEL_AVAILABLE = True
except ImportError as e:
    # Warning: Could not import trained model: {e}
    MODEL_AVAILABLE = False

# Import CNN detector as primary AI detection method
try:
    from predictor_model.cnn_text_classifier import CNNTextClassifier
    CNN_AVAILABLE = True
except ImportError as e:
    # Warning: Could not import CNN model: {e}
    CNN_AVAILABLE = False

# Import neural detector for AI detection (backup)
try:
    from .neural_detector import NeuralAIDetector
    NEURAL_AVAILABLE = True
except ImportError as e:
    # Warning: Could not import neural detector: {e}
    NEURAL_AVAILABLE = False

def detect_ai_content_enhanced(text: str) -> Dict[str, Union[str, float, List, Dict]]:
    """
    Enhanced AI content detection using CNN model as primary with neural model (RoBERTa) as backup.
    
    Args:
        text (str): Text content to analyze
    
    Returns:
        dict: Analysis results with detailed feedback
    """
    if not text or not text.strip():
        return {
            'error': 'Empty text provided',
            'ai_probability': 0,
            'human_probability': 0,
            'confidence': 0,
            'classification': 'Analysis Pending',
            'risk_level': 'Low',
            'analysis': {},
            'feedback_messages': ['Please provide text to analyze'],
            'flagged_sections': [],
            'recommendations': []
        }
    
    # Try CNN model first (primary)
    if CNN_AVAILABLE:
        try:
            cnn_classifier = CNNTextClassifier()
            cnn_result = cnn_classifier.predict(text)
            
            # Convert CNN result to enhanced format
            ai_prob = cnn_result['ai_probability']
            human_prob = cnn_result['human_probability']
            confidence = cnn_result['confidence']
            prediction = cnn_result['prediction']
            
            # Determine classification and risk level
            if ai_prob >= 0.8:
                classification = 'Likely AI-Generated'
                risk_level = 'High'
            elif ai_prob >= 0.6:
                classification = 'Possibly AI-Generated'
                risk_level = 'Medium'
            elif ai_prob >= 0.4:
                classification = 'Uncertain'
                risk_level = 'Medium'
            else:
                classification = 'Likely Human-Written'
                risk_level = 'Low'
            
            # Generate feedback messages
            feedback_messages = generate_feedback_messages(ai_prob, human_prob, text)
            
            # Identify flagged sections for highlighting
            flagged_sections = identify_flagged_sections(text, ai_prob)
            
            # Create consolidated flagged sections
            consolidated_section = create_consolidated_flagged_sections(flagged_sections)
            
            return {
                'ai_probability': ai_prob,
                'human_probability': human_prob,
                'confidence': confidence,
                'classification': classification,
                'risk_level': risk_level,
                'analysis': {
                    'prediction_method': 'cnn_primary',
                    'model_type': 'Character-based CNN',
                    'prediction': prediction
                },
                'feedback_messages': feedback_messages,
                'flagged_sections': flagged_sections,
                'consolidated_flagged_section': consolidated_section,
                'recommendations': generate_recommendations(ai_prob, classification)
            }
            
        except Exception as e:
            print(f"CNN model detection failed, falling back to neural model: {e}")
            # Fall through to neural detector backup
    
    # Use neural detector as backup
    if NEURAL_AVAILABLE:
        try:
            neural_detector = NeuralAIDetector()
            result = neural_detector.detect(text)
            
            # Add legacy compatibility fields if missing
            if 'analysis' not in result:
                result['analysis'] = {}
            result['analysis']['prediction_method'] = 'neural_backup'
            
            return result
            
        except Exception as e:
            print(f"Neural model detection failed: {e}")
            return {
                'error': f'Both CNN and neural model detection failed: {e}',
                'ai_probability': 0,
                'human_probability': 0,
                'confidence': 0,
                'classification': 'Analysis Failed',
                'risk_level': 'Error',
                'analysis': {'prediction_method': 'error'},
                'feedback_messages': ['Both detection models failed. Please try again.'],
                'flagged_sections': [],
                'recommendations': ['Check system status and try again']
            }
    
    # If no detectors are available, return error
    return {
        'error': 'No detection models available',
        'ai_probability': 0,
        'human_probability': 0,
        'confidence': 0,
        'classification': 'Analysis Failed',
        'risk_level': 'Error',
        'analysis': {'prediction_method': 'error'},
        'feedback_messages': ['No detection models available. System requires CNN or RoBERTa model.'],
        'flagged_sections': [],
        'recommendations': ['Contact system administrator']
    }

def generate_feedback_messages(ai_prob: float, human_prob: float, text: str) -> List[str]:
    """
    Generate detailed feedback messages based on prediction results.
    """
    messages = []
    
    if ai_prob >= 0.8:
        messages.append("⚠️ High AI probability detected. This text shows strong patterns typical of AI-generated content.")
        messages.append("🔍 Consider reviewing for authenticity if this is claimed to be human-written.")
    elif ai_prob >= 0.6:
        messages.append("⚡ Moderate AI probability detected. Some patterns suggest possible AI generation.")
        messages.append("📝 Manual review recommended to verify authorship.")
    elif ai_prob >= 0.4:
        messages.append("🤔 Uncertain classification. The text shows mixed characteristics.")
        messages.append("🔄 Consider additional context or longer text samples for better accuracy.")
    elif ai_prob >= 0.2:
        messages.append("✅ Low AI probability. Text appears to have human-like characteristics.")
        messages.append("👤 Likely written by a human author.")
    else:
        messages.append("✅ Very low AI probability. Strong indicators of human authorship.")
        messages.append("🎯 High confidence in human-written classification.")
    
    # Add text-specific insights
    word_count = len(text.split())
    if word_count < 50:
        messages.append("📏 Note: Short text samples may have reduced detection accuracy.")
    elif word_count > 500:
        messages.append("📚 Good text length for reliable detection analysis.")
    
    return messages

def identify_flagged_sections(text: str, ai_prob: float) -> List[Dict[str, Union[str, int, float]]]:
    """
    Identify specific sections of text that contribute to AI detection using comprehensive pattern analysis.
    Based on advanced AI detection research including repetition, consistency, style, and human touch analysis.
    """
    import re
    from collections import Counter
    
    flagged_sections = []
    
    # Enhanced sentence splitting that handles various punctuation
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
    
    # Calculate text-wide statistics for consistency analysis
    all_words = text.lower().split()
    word_freq = Counter(all_words)
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    
    # Comprehensive AI detection patterns
    ai_patterns = {
        # 1. Repetition & Redundancy
        'repetitive_phrases': {
            'patterns': [
                r'\b(it is important to|it should be noted|it is worth noting|research shows|studies indicate)\b',
                r'\b(in other words|that is to say|to put it simply|in essence)\b',
                r'\b(as mentioned|as stated|as discussed|as noted)\b'
            ],
            'weight': 0.4,
            'description': 'Repetitive explanatory phrases'
        },
        
        # 2. Formal Transitions (Enhanced)
        'mechanical_transitions': {
            'patterns': [
                r'\b(Furthermore|Moreover|Additionally|In addition|However|Nevertheless|Nonetheless|Therefore|Thus|Hence)\b',
                r'\b(Consequently|Subsequently|Meanwhile|Similarly|Likewise|Conversely|On the other hand)\b',
                r'\b(In conclusion|To conclude|In summary|To summarize|Overall|In essence|Ultimately)\b'
            ],
            'weight': 0.5,
            'description': 'Mechanical transition words'
        },
        
        # 3. AI Buzzwords & Jargon
        'ai_buzzwords': {
            'patterns': [
                r'\b(delve into|dive deep|unpack|leverage|utilize|optimize|streamline|facilitate|enhance)\b',
                r'\b(cutting-edge|state-of-the-art|revolutionary|groundbreaking|innovative|comprehensive)\b',
                r'\b(holistic|robust|scalable|seamless|efficient|significant|substantial|considerable)\b',
                r'\b(methodology|framework|paradigm|infrastructure|implementation|optimization)\b'
            ],
            'weight': 0.4,
            'description': 'AI-typical buzzwords and jargon'
        },
        
        # 4. Excessive Qualifiers & Hedging
        'hedging_language': {
            'patterns': [
                r'\b(potentially|possibly|likely|probably|generally|typically|usually|often|frequently)\b',
                r'\b(somewhat|rather|quite|fairly|relatively|comparatively|essentially|basically)\b',
                r'\b(may|might|could|would|should|tend to|appear to|seem to)\b'
            ],
            'weight': 0.3,
            'description': 'Excessive hedging and qualifiers'
        },
        
        # 5. Diplomatic & Safe Language
        'diplomatic_phrasing': {
            'patterns': [
                r'\b(it\'s important to consider|it\'s worth noting|it\'s crucial to understand)\b',
                r'\b(on one hand|on the other hand|while it\'s true|although it\'s important)\b',
                r'\b(balanced approach|comprehensive solution|holistic perspective|nuanced view)\b'
            ],
            'weight': 0.4,
            'description': 'Overly diplomatic phrasing'
        },
        
        # 6. Vague References
        'vague_references': {
            'patterns': [
                r'\b(research shows|studies indicate|experts suggest|data reveals|evidence suggests)\b',
                r'\b(it has been found|it is believed|it is generally accepted|it is widely known)\b',
                r'\b(many people|most experts|recent studies|various sources|numerous reports)\b'
            ],
            'weight': 0.4,
            'description': 'Vague references without sources'
        },
        
        # 7. Passive Voice (Enhanced)
        'passive_voice': {
            'patterns': [
                r'\b(is|are|was|were|been|being)\s+\w+ed\b',
                r'\b(can be|will be|has been|have been|had been|should be|could be)\s+\w+ed\b',
                r'\b(is considered|are regarded|was determined|were established)\b'
            ],
            'weight': 0.25,
            'description': 'Excessive passive voice'
        },
        
        # 8. Em-dash Overuse & Punctuation Patterns
        'punctuation_patterns': {
            'patterns': [
                r'—.*?—',  # Em-dash pairs
                r'[,;:]{3,}',  # Multiple punctuation marks
                r'\([^)]{20,}\)',  # Long parenthetical statements
            ],
            'weight': 0.3,
            'description': 'Excessive punctuation patterns'
        }
    }
    
    for i, sentence in enumerate(sentences):
        words = sentence.split()
        word_count = len(words)
        
        if word_count < 5:  # Skip very short sentences
            continue
            
        flag_score = 0
        reasons = []
        sentence_lower = sentence.lower()
        
        # Check each AI pattern
        for pattern_name, pattern_config in ai_patterns.items():
            pattern_matches = 0
            for pattern in pattern_config['patterns']:
                matches = len(re.findall(pattern, sentence, re.IGNORECASE))
                pattern_matches += matches
            
            if pattern_matches > 0:
                # Calculate score based on pattern density
                pattern_density = pattern_matches / word_count
                pattern_score = pattern_density * pattern_config['weight']
                flag_score += pattern_score
                
                if pattern_score > 0.08:  # Lower threshold for more sensitivity
                    reasons.append(f"{pattern_config['description']} ({pattern_matches} instances)")
        
        # Advanced Analysis Features
        
        # 1. Repetition Detection - REMOVED per user request (humans naturally repeat words for emphasis)
        
        # 2. Sentence Length Uniformity - REMOVED per user request
        
        # 3. Very Long Sentences - REMOVED per user request
        
        # 4. Lack of Human Touch - REMOVED per user request (incorrectly flags legitimate formal writing like academic papers)
        
        # 5. Em-dash Overuse
        em_dashes = sentence.count('—')
        if em_dashes > 1:
            flag_score += 0.3
            reasons.append(f'Excessive em-dashes ({em_dashes} instances)')
        
        # 6. Generic Sentence Starters
        sentence_start = ' '.join(words[:4]).lower()
        generic_starters = ['it is', 'this is', 'there are', 'there is', 'it can be', 'this can', 'one of the']
        if any(starter in sentence_start for starter in generic_starters):
            flag_score += 0.15
            reasons.append('Generic sentence starter')
        
        # 7. Perfect Grammar (Too Clean)
        # Check for lack of natural imperfections
        has_typos = bool(re.search(r'\b\w*[aeiou]{3,}\w*\b|\b\w*[bcdfghjklmnpqrstvwxyz]{3,}\w*\b', sentence_lower))
        if word_count > 20 and not has_typos and ',' in sentence and ';' not in sentence:
            flag_score += 0.1
            reasons.append('Overly polished grammar')
        
        # 8. Balanced/Safe Statements - REMOVED per user request
        
        # 9. Consistency Issues (Tone Switching)
        formal_indicators = len(re.findall(r'\b(shall|ought|thus|hence|therefore|furthermore)\b', sentence_lower))
        casual_indicators = len(re.findall(r'\b(gonna|wanna|kinda|sorta|yeah|nah|ok)\b', sentence_lower))
        
        if formal_indicators > 0 and casual_indicators > 0:
            flag_score += 0.25
            reasons.append('Mixed formal/casual tone')
        
        # Adjust threshold based on AI probability
        if ai_prob > 0.9:
            threshold = 0.15
        elif ai_prob > 0.7:
            threshold = 0.25
        elif ai_prob > 0.5:
            threshold = 0.35
        else:
            threshold = 0.45
        
        # Flag if score exceeds threshold
        if flag_score >= threshold and reasons:
            # Find actual position in original text
            start_pos = text.find(sentence)
            if start_pos == -1:  # Fallback if exact match not found
                # Try to find a partial match
                partial_sentence = sentence[:50] if len(sentence) > 50 else sentence
                start_pos = text.find(partial_sentence)
                if start_pos == -1:
                    start_pos = 0
            
            flagged_sections.append({
                'text': sentence.strip(),
                'start_position': start_pos,
                'end_position': start_pos + len(sentence),
                'flag_score': round(flag_score, 3),
                'reasons': reasons[:4],  # Limit to top 4 reasons
                'confidence': min(0.98, flag_score * 1.8),  # Convert score to confidence
                'word_count': word_count
            })
    
    # Sort by flag score (highest first) and return top sections
    flagged_sections.sort(key=lambda x: x['flag_score'], reverse=True)
    return flagged_sections[:10]  # Return up to 10 most suspicious sections

def create_consolidated_flagged_sections(flagged_sections: List[Dict]) -> Dict[str, Union[str, int, float, List]]:
    """
    Create a consolidated version of flagged sections separated by dots with summarized reasons.
    
    Args:
        flagged_sections: List of individual flagged sections
        
    Returns:
        dict: Consolidated section with combined text and summarized reasons
    """
    if not flagged_sections:
        return None
    
    # Combine all flagged section texts with separator
    combined_text = " ..... ".join([section['text'].strip() for section in flagged_sections])
    
    # Collect and summarize all reasons
    all_reasons = []
    for section in flagged_sections:
        all_reasons.extend(section.get('reasons', []))
    
    # Count and summarize reasons
    from collections import Counter
    reason_counts = Counter(all_reasons)
    
    # Create summarized reasons list
    summarized_reasons = []
    for reason, count in reason_counts.most_common():
        if count > 1:
            summarized_reasons.append(f"{reason} (found {count} times)")
        else:
            summarized_reasons.append(reason)
    
    # Calculate overall metrics
    total_flag_score = sum(section['flag_score'] for section in flagged_sections)
    avg_confidence = sum(section['confidence'] for section in flagged_sections) / len(flagged_sections)
    total_word_count = sum(section['word_count'] for section in flagged_sections)
    
    # Find overall start and end positions
    start_position = min(section['start_position'] for section in flagged_sections)
    end_position = max(section['end_position'] for section in flagged_sections)
    
    return {
        'text': combined_text,
        'start_position': start_position,
        'end_position': end_position,
        'flag_score': round(total_flag_score, 3),
        'reasons': summarized_reasons[:8],  # Limit to top 8 summarized reasons
        'confidence': round(avg_confidence, 3),
        'word_count': total_word_count,
        'section_count': len(flagged_sections),
        'type': 'consolidated'
    }

def generate_recommendations(ai_prob: float, classification: str) -> List[str]:
    """
    Generate recommendations based on AI probability and classification.
    """
    recommendations = []
    
    if ai_prob >= 0.8:
        recommendations.extend([
            "🔍 Verify the source and authorship of this content",
            "📋 Request additional documentation or proof of human authorship",
            "⚖️ Consider this result in your content evaluation process"
        ])
    elif ai_prob >= 0.6:
        recommendations.extend([
            "🤝 Engage in direct communication with the claimed author",
            "📝 Request clarification on specific sections if needed",
            "🔍 Look for additional context clues about authorship"
        ])
    elif ai_prob >= 0.4:
        recommendations.extend([
            "📊 Consider the overall context and purpose of the content",
            "🔄 Additional analysis may be helpful for uncertain cases"
        ])
    else:
        recommendations.extend([
            "✅ Content appears to be human-written",
            "📚 Use this as a baseline for comparing similar content"
        ])
    
    recommendations.append("💡 Remember: AI detection is probabilistic, not definitive")
    return recommendations

def generate_enhanced_recommendations(ai_prob: float, text: str) -> List[str]:
    """
    Generate actionable recommendations based on detection results.
    """
    recommendations = []
    
    if ai_prob >= 0.7:
        recommendations.extend([
            "🔍 Verify the source and authorship of this content",
            "📋 Request additional documentation or proof of human authorship",
            "⚖️ Consider this result in your content evaluation process",
            "🔄 Cross-reference with other AI detection tools for confirmation"
        ])
    elif ai_prob >= 0.4:
        recommendations.extend([
            "🤝 Engage in direct communication with the claimed author",
            "📝 Request clarification on specific sections if needed",
            "🔍 Look for additional context clues about authorship",
            "📊 Consider the overall context and purpose of the content"
        ])
    else:
        recommendations.extend([
            "✅ Content appears to be human-written",
            "📚 Use this as a baseline for comparing similar content",
            "🎯 High confidence in human authorship classification"
        ])
    
    # General recommendations
    recommendations.append("💡 Remember: AI detection is probabilistic, not definitive")
    recommendations.append("🔬 Combine with other evaluation methods for best results")
    
    return recommendations