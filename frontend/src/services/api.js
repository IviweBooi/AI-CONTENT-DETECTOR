/**
 * API Service for AI Content Detector
 * 
 * This file contains simulated API calls that will be replaced with actual
 * backend calls when the backend is implemented.
 */

// Base API URL - backend server
// Use environment variable for production, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Check if we should use mock API (disabled by default, backend is available)
const USE_MOCK_API = false;

// Simulate network delay for more realistic API call experience
const simulateNetworkDelay = (minMs = 500, maxMs = 1500) => {
  // In test environment, bypass delay completely
  if (process.env.NODE_ENV === 'test') {
    return Promise.resolve();
  }
  
  const delay = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return new Promise(resolve => setTimeout(resolve, delay));
};

/**
 * Analyze text content for AI detection
 * 
 * @param {string} text - The text content to analyze
 * @returns {Promise<Object>} - Analysis results
 */
export const analyzeText = async (text) => {
  try {
    // Check for empty text
    if (!text || text.trim().length === 0) {
      return {
        success: false,
        error: 'Please provide text to analyze.'
      };
    }

    // Simulate network delay
    await simulateNetworkDelay();
    
    // In a real implementation, this would be a fetch call to the backend
    // return await fetch(`${API_BASE_URL}/analyze`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ text })
    // }).then(res => res.json());
    
    // For now, simulate a response based on text length for deterministic results
    const seed = Math.min(1000, text.trim().length);
    const base = (seed % 87) + 10; // 10 - 96
    const aiLikelihood = Math.min(99, Math.round(base * 0.78));
    const perplex = (120 - (base % 60)).toFixed(1);
    const burst = (2.2 + (base % 30) / 20).toFixed(1);
    
    return {
      success: true,
      data: {
        overall: base,
        ai_probability: aiLikelihood,
        metrics: { perplexity: perplex, burstiness: burst },
        metricsBars: {
          structure: (50 + (base % 45)),
          vocabulary: (40 + (base % 50)),
          style: (30 + (base % 60)),
        },
        flaggedSections: generateFlaggedSections(text),
        text: text
      }
    };
  } catch (error) {
    console.error('Error analyzing text:', error);
    return {
      success: false,
      error: 'Failed to analyze text. Please try again.'
    };
  }
};

/**
 * Upload and analyze a file
 * 
 * @param {File} file - The file to upload and analyze
 * @returns {Promise<Object>} - Analysis results and file info
 */
export const analyzeFile = async (file) => {
  try {
    // Check for null or invalid file
    if (!file) {
      return {
        success: false,
        error: 'Please provide a valid file to analyze.'
      };
    }

    // Use mock data if backend is not available (e.g., on Netlify)
    if (USE_MOCK_API) {
      await simulateNetworkDelay();
      
      // Mock file content extraction
      const mockText = file.type === 'application/pdf' 
        ? 'This is extracted text from a PDF file. Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        : file.type.startsWith('image/') 
        ? 'This is extracted text from an image using OCR. Sample text content.'
        : 'This is extracted text from the uploaded file.';
      
      const extractedText = mockText;
      
      return {
        success: true,
        data: {
          text: extractedText,
          result: {
            ai_probability: Math.random() * 0.4 + 0.3, // Random between 0.3-0.7
            confidence: Math.random() * 0.3 + 0.7, // Random between 0.7-1.0
            analysis: {
              patterns: ['repetitive_structure', 'formal_language'],
              indicators: {
                vocabulary_complexity: Math.random() * 0.5 + 0.5,
                sentence_structure: Math.random() * 0.4 + 0.4,
                coherence: Math.random() * 0.3 + 0.6
              }
            }
          },
          fileInfo: {
            name: file.name,
            size: file.size,
            type: file.type
          }
        }
      };
    }
    
    // Create FormData to upload the file
    const formData = new FormData();
    formData.append('file', file);
    
    // Upload file to backend
     const response = await fetch(`${API_BASE_URL}/detect`, {
       method: 'POST',
       body: formData
     });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
     
     // Return the extracted text and file info for analysis
     // Handle case where content field might be missing from backend response
     const extractedText = data.content || data.text || '';
     
      return {
        success: true,
        data: {
          text: extractedText,
          result: data.result,
          fileInfo: {
            name: file.name,
            size: file.size,
            type: file.type,
          }
        }
      };
  } catch (error) {
    console.error('Error analyzing file:', error);
    return {
      success: false,
      error: error.message || 'Failed to analyze file. Please try again.'
    };
  }
};

/**
 * Submit user feedback about analysis results
 * 
 * @param {Object} feedback - The feedback data
 * @param {string} feedback.type - Feedback type (Accurate, Partially Accurate, Inaccurate)
 * @param {string} feedback.comment - Additional comments
 * @param {string} feedback.resultId - ID of the analysis result being rated (optional)
 * @returns {Promise<Object>} - Submission confirmation
 */
export const submitFeedback = async (feedback) => {
  try {
    // Validate feedback
    if (!feedback || !feedback.type) {
      return {
        success: false,
        error: 'Feedback type is required.'
      };
    }

    // Simulate network delay
    await simulateNetworkDelay();
    
    // In a real implementation, this would be a fetch call to the backend
    // return await fetch(`${API_BASE_URL}/feedback`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(feedback)
    // }).then(res => res.json());
    
    console.log('Feedback submitted:', feedback);
    
    return {
      success: true,
      message: 'Thank you for your feedback!'
    };
  } catch (error) {
    console.error('Error submitting feedback:', error);
    return {
      success: false,
      error: 'Failed to submit feedback. Please try again.'
    };
  }
};

/**
 * Track scan count for analytics
 * 
 * @param {Object} scanData - Data about the scan
 * @param {string} scanData.contentType - Type of content (text, file)
 * @param {number} scanData.contentLength - Length of analyzed content
 * @returns {Promise<Object>} - Tracking confirmation
 */
export const trackScan = async (scanData = {}) => {
  try {
    // In a real implementation, this would be a fetch call to the backend
    // return await fetch(`${API_BASE_URL}/analytics/scan`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(scanData)
    // }).then(res => res.json());
    
    console.log('Scan tracked:', scanData);
    
    return {
      success: true
    };
  } catch (error) {
    console.error('Error tracking scan:', error);
    // Fail silently - don't affect user experience if analytics fails
    return {
      success: false
    };
  }
};

/**
 * Export analysis results as a report
 * 
 * @param {Object} result - The analysis result to export
 * @param {string} format - Export format (pdf, json, txt)
 * @returns {Promise<Object>} - URL or blob of the exported report
 */
export const exportReport = async (result, format = 'pdf') => {
  try {
    // Validate input
    if (!result) {
      return {
        success: false,
        error: 'Missing result data for export'
      };
    }

    // Simulate network delay
    await simulateNetworkDelay(1500, 3000);
    
    // In a real implementation, this would be a fetch call to the backend
    // return await fetch(`${API_BASE_URL}/export`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ result, format })
    // }).then(res => res.blob());
    
    console.log(`Exporting report in ${format} format:`, result);
    
    return {
      success: true,
      data: {
        url: `https://example.com/reports/sample-${Date.now()}.${format}`,
        format: format
      },
      message: `Report exported in ${format} format`
    };
  } catch (error) {
    console.error('Error exporting report:', error);
    return {
      success: false,
      error: 'Failed to export report. Please try again.'
    };
  }
};

// Helper function to extract text from a file (client-side)
// In a real implementation, this would be handled by the backend
const extractTextFromFile = async (file) => {
  if (file.name.toLowerCase().endsWith('.pdf')) {
    // Simple text extraction for demo
    const arrayBuffer = await file.arrayBuffer();
    const text = new TextDecoder('utf-8').decode(arrayBuffer);
    return text;
  } else if (file.name.toLowerCase().endsWith('.docx')) {
    // Simple text extraction for demo
    const arrayBuffer = await file.arrayBuffer();
    const text = new TextDecoder('utf-8').decode(arrayBuffer);
    return text.replace(/[^\x20-\x7E\n\r\t]/g, '');
  } else {
    // For TXT files
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        resolve(String(e.target.result || ''));
      };
      reader.readAsText(file);
    });
  }
};

// Helper function to generate mock flagged sections
const generateFlaggedSections = (text) => {
  // In a real implementation, this would come from the backend analysis
  const sentences = text.replace(/\n+/g, ' ').split(/(?<=[.!?])\s+/).filter(Boolean);
  
  // Select a few sentences to flag as AI-generated
  const flagged = [];
  if (sentences.length > 3) {
    // Flag approximately 20% of sentences
    const numToFlag = Math.max(1, Math.floor(sentences.length * 0.2));
    const indices = new Set();
    
    while (indices.size < numToFlag) {
      const idx = Math.floor(Math.random() * sentences.length);
      indices.add(idx);
    }
    
    // Create flagged sections with confidence scores
    [...indices].forEach(idx => {
      flagged.push({
        text: sentences[idx],
        confidence: Math.floor(Math.random() * 30) + 70, // 70-99% confidence
        reason: getRandomFlagReason()
      });
    });
  }
  
  return flagged;
};

// Helper function to generate random flag reasons
const getRandomFlagReason = () => {
  const reasons = [
    'Repetitive sentence structure',
    'Unusual word patterns',
    'Statistical language anomalies',
    'Predictable phrasing',
    'Low perplexity score',
    'High burstiness pattern'
  ];
  
  return reasons[Math.floor(Math.random() * reasons.length)];
};