/**
 * API Service for AI Content Detector
 * 
 * This file contains simulated API calls that will be replaced with actual
 * backend calls when the backend is implemented.
 */

// Base API URL - would be replaced with actual backend URL in production
// const API_BASE_URL = process.env.NODE_ENV === 'production' 
//   ? 'https://api.ai-content-detector.com/v1'
//   : 'http://localhost:5000/api/v1';
// Commented out as it's not used in the current simulation

// Simulate network delay for more realistic API call experience
const simulateNetworkDelay = (minMs = 500, maxMs = 1500) => {
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
        aiLikelihood,
        metrics: { perplexity: perplex, burstiness: burst },
        metricsBars: {
          structure: (50 + (base % 45)),
          vocabulary: (40 + (base % 50)),
          style: (30 + (base % 60)),
        },
        flaggedSections: generateFlaggedSections(text),
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
    // Simulate network delay
    await simulateNetworkDelay(1000, 2500); // Longer delay for file upload simulation
    
    // In a real implementation, this would use FormData to upload the file
    // const formData = new FormData();
    // formData.append('file', file);
    // 
    // return await fetch(`${API_BASE_URL}/analyze/file`, {
    //   method: 'POST',
    //   body: formData
    // }).then(res => res.json());
    
    // For now, extract text from the file client-side and simulate a response
    const fileContent = await extractTextFromFile(file);
    const result = await analyzeText(fileContent);
    
    return {
      ...result,
      fileInfo: {
        name: file.name,
        size: file.size,
        type: file.type,
      }
    };
  } catch (error) {
    console.error('Error analyzing file:', error);
    return {
      success: false,
      error: 'Failed to analyze file. Please try again.'
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
      message: `Report exported in ${format} format`,
      // In a real implementation, this would be a blob or download URL
      // downloadUrl: URL.createObjectURL(blob)
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