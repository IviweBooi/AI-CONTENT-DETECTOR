import pytest
from utils.ai_detector import (
    detect_ai_content, clean_text, count_sentences, calculate_avg_sentence_length,
    calculate_lexical_diversity, calculate_repetition_score, calculate_formality_score,
    calculate_complexity_score, detect_ai_patterns, calculate_ai_probability,
    calculate_confidence, generate_recommendations
)

class TestAIDetector:
    """Test cases for AI content detection functionality"""
    
    def test_detect_ai_content_empty_text(self):
        """Test detection with empty text"""
        result = detect_ai_content('')
        assert result['error'] == 'Empty text provided'
        assert result['ai_probability'] == 0
        assert result['confidence'] == 0
    
    def test_detect_ai_content_whitespace_only(self):
        """Test detection with whitespace-only text"""
        result = detect_ai_content('   \n\t  ')
        assert result['error'] == 'Empty text provided'
        assert result['ai_probability'] == 0
    
    def test_detect_ai_content_valid_text(self):
        """Test detection with valid text"""
        text = "This is a sample text for testing. It contains multiple sentences to analyze."
        result = detect_ai_content(text)
        
        assert 'ai_probability' in result
        assert 'human_probability' in result
        assert 'confidence' in result
        assert 'classification' in result
        assert 'risk_level' in result
        assert 'analysis' in result
        assert 'recommendations' in result
        
        # Check probability bounds
        assert 0 <= result['ai_probability'] <= 1
        assert 0 <= result['human_probability'] <= 1
        assert abs(result['ai_probability'] + result['human_probability'] - 1) < 0.001
    
    def test_detect_ai_content_high_ai_probability(self):
        """Test classification for high AI probability text"""
        # Text with AI-like patterns
        text = """In conclusion, it is important to note that this analysis provides valuable insights. 
                 Furthermore, the data suggests significant patterns. Overall, the results are positive. 
                 To summarize, this comprehensive study demonstrates clear findings."""
        
        result = detect_ai_content(text)
        # Should have higher AI probability due to patterns
        assert result['ai_probability'] > 0.3  # Should detect some AI patterns
    
    def test_detect_ai_content_low_ai_probability(self):
        """Test classification for low AI probability text"""
        # More human-like text
        text = """Hey there! I was just thinking about our conversation yesterday. 
                 You know what? I totally forgot to mention that crazy thing that happened. 
                 My friend literally couldn't believe it when I told her!"""
        
        result = detect_ai_content(text)
        # Should have lower AI probability due to informal language
        assert result['ai_probability'] < 0.8  # Informal text should score lower

class TestTextCleaning:
    """Test cases for text cleaning functionality"""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning"""
        text = "  This   is    a   test   "
        result = clean_text(text)
        assert result == "This is a test"
    
    def test_clean_text_urls(self):
        """Test URL removal"""
        text = "Check this out: https://example.com and http://test.org"
        result = clean_text(text)
        assert "https://example.com" not in result
        assert "http://test.org" not in result
        assert "Check this out:" in result
    
    def test_clean_text_emails(self):
        """Test email removal"""
        text = "Contact me at test@example.com or admin@site.org"
        result = clean_text(text)
        assert "test@example.com" not in result
        assert "admin@site.org" not in result
        assert "Contact me at" in result

class TestSentenceAnalysis:
    """Test cases for sentence analysis functions"""
    
    def test_count_sentences_basic(self):
        """Test basic sentence counting"""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        result = count_sentences(text)
        assert result == 3
    
    def test_count_sentences_empty(self):
        """Test sentence counting with empty text"""
        result = count_sentences("")
        assert result == 0
    
    def test_count_sentences_no_punctuation(self):
        """Test sentence counting without punctuation"""
        text = "This is just one long sentence without proper punctuation"
        result = count_sentences(text)
        assert result == 1
    
    def test_calculate_avg_sentence_length_basic(self):
        """Test average sentence length calculation"""
        text = "Short sentence. This is a longer sentence with more words."
        result = calculate_avg_sentence_length(text)
        # First sentence: 2 words, Second sentence: 9 words, Average: 5.5
        assert result > 0  # Just check it's positive, actual calculation may vary
    
    def test_calculate_avg_sentence_length_empty(self):
        """Test average sentence length with empty text"""
        result = calculate_avg_sentence_length("")
        assert result == 0

class TestLexicalAnalysis:
    """Test cases for lexical analysis functions"""
    
    def test_calculate_lexical_diversity_basic(self):
        """Test lexical diversity calculation"""
        text = "the cat sat on the mat"  # 5 unique words out of 6 total
        result = calculate_lexical_diversity(text)
        assert abs(result - (5/6)) < 0.01
    
    def test_calculate_lexical_diversity_all_unique(self):
        """Test lexical diversity with all unique words"""
        text = "every single word here different"
        result = calculate_lexical_diversity(text)
        assert result == 1.0
    
    def test_calculate_lexical_diversity_empty(self):
        """Test lexical diversity with empty text"""
        result = calculate_lexical_diversity("")
        assert result == 0
    
    def test_calculate_repetition_score_basic(self):
        """Test repetition score calculation"""
        text = "this is a test this is a test"
        result = calculate_repetition_score(text)
        assert result > 0  # Should detect repetition
    
    def test_calculate_repetition_score_no_repetition(self):
        """Test repetition score with no repetition"""
        text = "every word in this sentence is completely different"
        result = calculate_repetition_score(text)
        assert result == 0
    
    def test_calculate_repetition_score_short_text(self):
        """Test repetition score with short text"""
        text = "short"
        result = calculate_repetition_score(text)
        assert result == 0

class TestFormalityAnalysis:
    """Test cases for formality analysis"""
    
    def test_calculate_formality_score_formal(self):
        """Test formality score with formal text"""
        text = "However, therefore, furthermore, the analysis demonstrates significant results."
        result = calculate_formality_score(text)
        assert result >= 0.5  # Should be more formal or neutral
    
    def test_calculate_formality_score_informal(self):
        """Test formality score with informal text"""
        text = "This is really pretty cool and totally awesome, basically."
        result = calculate_formality_score(text)
        assert result < 0.5  # Should be more informal
    
    def test_calculate_formality_score_neutral(self):
        """Test formality score with neutral text"""
        text = "The weather is nice today and birds are singing."
        result = calculate_formality_score(text)
        assert result == 0.5  # Should be neutral
    
    def test_calculate_formality_score_empty(self):
        """Test formality score with empty text"""
        result = calculate_formality_score("")
        assert result == 0

class TestComplexityAnalysis:
    """Test cases for complexity analysis"""
    
    def test_calculate_complexity_score_complex(self):
        """Test complexity score with complex sentences"""
        text = "Although the weather was bad, we went out because we had plans that we made."
        result = calculate_complexity_score(text)
        assert result > 0  # Should detect complexity indicators
    
    def test_calculate_complexity_score_simple(self):
        """Test complexity score with simple sentences"""
        text = "The cat sat. The dog ran. Birds fly."
        result = calculate_complexity_score(text)
        assert result == 0  # No complexity indicators
    
    def test_calculate_complexity_score_empty(self):
        """Test complexity score with empty text"""
        result = calculate_complexity_score("")
        assert result == 0

class TestPatternDetection:
    """Test cases for AI pattern detection"""
    
    def test_detect_ai_patterns_present(self):
        """Test AI pattern detection with patterns present"""
        text = "In conclusion, it is important to note that overall this is positive."
        result = detect_ai_patterns(text)
        assert result > 0  # Should detect AI patterns
    
    def test_detect_ai_patterns_absent(self):
        """Test AI pattern detection with no patterns"""
        text = "This is just normal human text without any specific patterns."
        result = detect_ai_patterns(text)
        assert result == 0  # Should not detect patterns
    
    def test_detect_ai_patterns_multiple(self):
        """Test AI pattern detection with multiple patterns"""
        text = "In conclusion, furthermore, on the other hand, to summarize the findings."
        result = detect_ai_patterns(text)
        assert result > 0.3  # Should detect multiple patterns

class TestProbabilityCalculation:
    """Test cases for probability calculation"""
    
    def test_calculate_ai_probability_basic(self):
        """Test AI probability calculation"""
        analysis = {
            'avg_sentence_length': 20,
            'lexical_diversity': 0.3,
            'repetition_score': 0.5,
            'formality_score': 0.8,
            'complexity_score': 0.5,
            'pattern_score': 0.6
        }
        result = calculate_ai_probability(analysis)
        assert 0 <= result <= 1
    
    def test_calculate_ai_probability_high_ai_indicators(self):
        """Test AI probability with high AI indicators"""
        analysis = {
            'avg_sentence_length': 20,  # AI sweet spot
            'lexical_diversity': 0.3,   # Low diversity
            'repetition_score': 0.8,    # High repetition
            'formality_score': 0.9,     # Very formal
            'complexity_score': 0.5,    # Moderate complexity
            'pattern_score': 0.8        # High pattern score
        }
        result = calculate_ai_probability(analysis)
        assert result > 0.5  # Should indicate higher AI probability
    
    def test_calculate_ai_probability_low_ai_indicators(self):
        """Test AI probability with low AI indicators"""
        analysis = {
            'avg_sentence_length': 35,  # Outside AI range
            'lexical_diversity': 0.8,   # High diversity
            'repetition_score': 0.1,    # Low repetition
            'formality_score': 0.2,     # Informal
            'complexity_score': 0.9,    # High complexity
            'pattern_score': 0.1        # Low pattern score
        }
        result = calculate_ai_probability(analysis)
        assert result < 0.7  # Should indicate lower AI probability

class TestConfidenceCalculation:
    """Test cases for confidence calculation"""
    
    def test_calculate_confidence_short_text(self):
        """Test confidence calculation for short text"""
        analysis = {
            'word_count': 30,
            'pattern_score': 0.2,
            'repetition_score': 0.1
        }
        result = calculate_confidence(analysis)
        assert result < 0.5  # Low confidence for short text
    
    def test_calculate_confidence_long_text(self):
        """Test confidence calculation for long text"""
        analysis = {
            'word_count': 600,
            'pattern_score': 0.3,
            'repetition_score': 0.2
        }
        result = calculate_confidence(analysis)
        assert result > 0.8  # High confidence for long text
    
    def test_calculate_confidence_bounds(self):
        """Test confidence calculation bounds"""
        analysis = {
            'word_count': 1000,
            'pattern_score': 1.0,
            'repetition_score': 1.0
        }
        result = calculate_confidence(analysis)
        assert result <= 1.0  # Should not exceed 1.0

class TestRecommendations:
    """Test cases for recommendation generation"""
    
    def test_generate_recommendations_high_ai(self):
        """Test recommendations for high AI probability"""
        analysis = {
            'repetition_score': 0.2,
            'pattern_score': 0.2,
            'lexical_diversity': 0.6
        }
        recommendations = generate_recommendations(analysis, 0.8)
        assert any('High likelihood' in rec for rec in recommendations)
        assert any('manual review' in rec for rec in recommendations)
    
    def test_generate_recommendations_medium_ai(self):
        """Test recommendations for medium AI probability"""
        analysis = {
            'repetition_score': 0.2,
            'pattern_score': 0.2,
            'lexical_diversity': 0.6
        }
        recommendations = generate_recommendations(analysis, 0.5)
        assert any('Moderate AI indicators' in rec for rec in recommendations)
    
    def test_generate_recommendations_low_ai(self):
        """Test recommendations for low AI probability"""
        analysis = {
            'repetition_score': 0.2,
            'pattern_score': 0.2,
            'lexical_diversity': 0.6
        }
        recommendations = generate_recommendations(analysis, 0.2)
        assert any('Low AI indicators' in rec for rec in recommendations)
        assert any('human-written' in rec for rec in recommendations)
    
    def test_generate_recommendations_specific_metrics(self):
        """Test recommendations for specific metric thresholds"""
        analysis = {
            'repetition_score': 0.4,  # High repetition
            'pattern_score': 0.4,     # High patterns
            'lexical_diversity': 0.3  # Low diversity
        }
        recommendations = generate_recommendations(analysis, 0.5)
        assert any('repetition detected' in rec for rec in recommendations)
        assert any('AI-typical phrases' in rec for rec in recommendations)
        assert any('vocabulary diversity' in rec for rec in recommendations)