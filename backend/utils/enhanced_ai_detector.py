import os
import sys
from typing import Dict, List, Union

# Add predictor_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'predictor_model'))

try:
    from predictor_model.ai_text_classifier import AITextClassifier
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import trained model: {e}")
    MODEL_AVAILABLE = False

# Import ensemble detector for improved accuracy
try:
    from .ensemble_detector import EnsembleAIDetector
    ENSEMBLE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ensemble detector: {e}")
    ENSEMBLE_AVAILABLE = False

# Import rule-based detector for fallback
try:
    from .rule_based_detector import RuleBasedAIDetector
    RULE_BASED_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import rule-based detector: {e}")
    RULE_BASED_AVAILABLE = False

def detect_ai_content_enhanced(text: str) -> Dict[str, Union[str, float, List, Dict]]:
    """
    Enhanced AI content detection using ensemble method combining neural model and rule-based analysis.
    
    Args:
        text (str): Text content to analyze
    
    Returns:
        dict: Enhanced analysis results with detailed feedback
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
    
    # Try ensemble detection first (most accurate)
    if ENSEMBLE_AVAILABLE:
        try:
            ensemble_detector = EnsembleAIDetector()
            result = ensemble_detector.detect(text)
            
            # Add legacy compatibility fields if missing
            if 'analysis' not in result:
                result['analysis'] = {}
            result['analysis']['prediction_method'] = 'ensemble'
            
            return result
            
        except Exception as e:
            print(f"Ensemble detection failed, falling back to neural model: {e}")
    
    # Fallback to rule-based detection when neural model is unavailable
    if not MODEL_AVAILABLE and RULE_BASED_AVAILABLE:
        try:
            rule_detector = RuleBasedAIDetector()
            rule_result = rule_detector.analyze_text(text)
            
            ai_prob = rule_result['ai_probability']
            human_prob = 1 - ai_prob
            confidence = rule_result['confidence']
            
            # Enhanced classification with more granular levels
            if ai_prob >= 0.8:
                classification = 'Highly Likely AI-Generated'
                risk_level = 'Very High'
            elif ai_prob >= 0.6:
                classification = 'Likely AI-Generated'
                risk_level = 'High'
            elif ai_prob >= 0.4:
                classification = 'Possibly AI-Generated'
                risk_level = 'Medium'
            elif ai_prob >= 0.2:
                classification = 'Likely Human-Written'
                risk_level = 'Low'
            else:
                classification = 'Highly Likely Human-Written'
                risk_level = 'Very Low'
            
            # Generate feedback messages
            feedback_messages = [
                f"📋 Analysis completed using rule-based detection (neural model unavailable)",
                f"🎯 AI probability: {ai_prob:.1%}",
                f"📊 Confidence: {confidence:.1%}"
            ]
            
            # Add rule-based flags as feedback
            if rule_result.get('flags'):
                feedback_messages.extend([f"⚠️ {flag}" for flag in rule_result['flags'][:3]])
            
            # Add reasoning as feedback
            if rule_result.get('reasoning'):
                feedback_messages.extend([f"💡 {reason}" for reason in rule_result['reasoning'][:2]])
            
            # Convert flags to flagged sections
            flagged_sections = []
            if rule_result.get('flags'):
                for flag in rule_result['flags']:
                    flagged_sections.append({
                        'type': 'rule_based_flag',
                        'description': flag,
                        'source': 'rule_based_detector'
                    })
            
            # Generate recommendations
            recommendations = [
                "Analysis based on rule-based detection patterns",
                "Neural model unavailable - results may be less accurate",
                "Consider providing longer text for better analysis"
            ]
            
            # Additional analysis metrics
            analysis = {
                'word_count': len(text.split()),
                'sentence_count': len([s for s in text.split('.') if s.strip()]),
                'avg_sentence_length': len(text.split()) / max(len([s for s in text.split('.') if s.strip()]), 1),
                'prediction_method': 'rule_based_fallback',
                'features': rule_result.get('features', {})
            }
            
            return {
                'ai_probability': round(ai_prob, 3),
                'human_probability': round(human_prob, 3),
                'confidence': round(confidence, 3),
                'classification': classification,
                'risk_level': risk_level,
                'analysis': analysis,
                'feedback_messages': feedback_messages,
                'flagged_sections': flagged_sections,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Rule-based detection also failed: {e}")
            return {
                'error': 'AI detection models are currently unavailable. Please check installation and try again.',
                'ai_probability': 0,
                'human_probability': 0,
                'confidence': 0,
                'classification': 'Model Unavailable',
                'risk_level': 'Service Unavailable',
                'analysis': {'prediction_method': 'model_unavailable'},
                'feedback_messages': ['⚠️ AI detection models are currently unavailable. Please contact support or try again later.'],
                'flagged_sections': [],
                'recommendations': ['Check model installation and configuration']
            }
    
    try:
        # Use roberta-base-openai-detector model (working model)
        detector = AITextClassifier("roberta-base-openai-detector")
        result = detector.predict(text)
        
        ai_prob = result['ai_probability']
        human_prob = result['human_probability']
        model_confidence = result['confidence']  # Use actual model confidence
        
        # Enhanced classification with more granular levels
        if ai_prob >= 0.8:
            classification = 'Highly Likely AI-Generated'
            risk_level = 'Very High'
        elif ai_prob >= 0.6:
            classification = 'Likely AI-Generated'
            risk_level = 'High'
        elif ai_prob >= 0.4:
            classification = 'Possibly AI-Generated'
            risk_level = 'Medium'
        elif ai_prob >= 0.2:
            classification = 'Likely Human-Written'
            risk_level = 'Low'
        else:
            classification = 'Highly Likely Human-Written'
            risk_level = 'Very Low'
        
        # Generate detailed feedback
        feedback_messages = generate_feedback_messages(ai_prob, human_prob, text)
        flagged_sections = identify_flagged_sections(text, ai_prob)
        recommendations = generate_enhanced_recommendations(ai_prob, text)
        
        # Additional analysis metrics
        analysis = {
            'word_count': len(text.split()),
            'sentence_count': len([s for s in text.split('.') if s.strip()]),
            'avg_sentence_length': len(text.split()) / max(len([s for s in text.split('.') if s.strip()]), 1),
            'model_confidence': model_confidence,
            'prediction_method': 'neural_model_fallback'
        }
        
        return {
            'ai_probability': round(ai_prob, 3),
            'human_probability': round(human_prob, 3),
            'confidence': round(model_confidence, 3),
            'classification': classification,
            'risk_level': risk_level,
            'analysis': analysis,
            'feedback_messages': feedback_messages,
            'flagged_sections': flagged_sections,
            'recommendations': recommendations
        }
        
    except Exception as e:
        return {
            'error': f'AI detection failed: {str(e)}',
            'ai_probability': 0,
            'human_probability': 0,
            'confidence': 0,
            'classification': 'Detection Error',
            'risk_level': 'Analysis Failed',
            'analysis': {'prediction_method': 'error', 'error_details': str(e)},
            'feedback_messages': [f'⚠️ Detection failed: {str(e)}', '🔧 Please check configuration and try again.'],
            'flagged_sections': [],
            'recommendations': ['Check model files and dependencies', 'Verify installation', 'Contact technical support if issue persists']
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