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

# Import neural detector for AI detection
try:
    from .neural_detector import NeuralAIDetector
    NEURAL_AVAILABLE = True
except ImportError as e:
    # Warning: Could not import neural detector: {e}
    NEURAL_AVAILABLE = False

def detect_ai_content_enhanced(text: str) -> Dict[str, Union[str, float, List, Dict]]:
    """
    Enhanced AI content detection using neural model (RoBERTa) for accurate analysis.
    
    Args:
        text (str): Text content to analyze
    
    Returns:
        dict: Neural analysis results with detailed feedback
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
    
    # Use neural-only detection
    if NEURAL_AVAILABLE:
        try:
            neural_detector = NeuralAIDetector()
            result = neural_detector.detect(text)
            
            # Add legacy compatibility fields if missing
            if 'analysis' not in result:
                result['analysis'] = {}
            result['analysis']['prediction_method'] = 'neural_only'
            
            return result
            
        except Exception as e:
            print(f"Neural model detection failed: {e}")
            return {
                'error': f'Neural model detection failed: {e}',
                'ai_probability': 0,
                'human_probability': 0,
                'confidence': 0,
                'classification': 'Analysis Failed',
                'risk_level': 'Error',
                'analysis': {'prediction_method': 'error'},
                'feedback_messages': ['Neural model detection failed. Please try again.'],
                'flagged_sections': [],
                'recommendations': ['Check system status and try again']
            }
    
    # If neural detector is not available, return error
    return {
        'error': 'Neural model not available',
        'ai_probability': 0,
        'human_probability': 0,
        'confidence': 0,
        'classification': 'Analysis Failed',
        'risk_level': 'Error',
        'analysis': {'prediction_method': 'error'},
        'feedback_messages': ['Neural model not available. System requires RoBERTa model.'],
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
    Identify specific sections of text that contribute to AI detection.
    """
    flagged_sections = []
    
    # Simple sentence-level analysis (can be enhanced with attention weights)
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    for i, sentence in enumerate(sentences):
        if len(sentence.split()) < 3:  # Skip very short sentences
            continue
            
        # Heuristic flagging based on patterns
        flag_score = 0
        reasons = []
        
        # Check for AI-typical patterns
        if any(phrase in sentence.lower() for phrase in ['in conclusion', 'furthermore', 'moreover', 'additionally']):
            flag_score += 0.3
            reasons.append('Formal transition words')
        
        if len(sentence.split()) > 25:  # Very long sentences
            flag_score += 0.2
            reasons.append('Unusually long sentence')
        
        if sentence.count(',') > 3:  # Complex punctuation
            flag_score += 0.2
            reasons.append('Complex sentence structure')
        
        # Only flag if significant and AI probability is high
        if flag_score > 0.3 and ai_prob > 0.5:
            flagged_sections.append({
                'text': sentence,
                'start_position': text.find(sentence),
                'end_position': text.find(sentence) + len(sentence),
                'flag_score': round(flag_score, 2),
                'reasons': reasons
            })
    
    return flagged_sections[:5]  # Limit to top 5 flagged sections

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