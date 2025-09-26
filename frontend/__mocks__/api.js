/**
 * Mock API Service for testing
 * This mock avoids import.meta.env issues in Jest
 */

// Mock API URLs for testing
const API_BASE_URL = 'http://localhost:5001/api';
const ANALYTICS_API_URL = 'http://localhost:5002';

/**
 * Get analytics statistics
 */
export const getAnalyticsStats = async () => {
  const response = await fetch(`${ANALYTICS_API_URL}/analytics/health`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!response.ok) {
    throw new Error(`Analytics stats request failed: ${response.status}`);
  }
  
  const data = await response.json();
  return {
    success: true,
    data: data
  };
};

/**
 * Analyze text for AI content detection
 */
export const analyzeText = async (text) => {
  try {
    if (!text || text.trim().length === 0) {
      return {
        success: false,
        error: 'Please provide text to analyze.'
      };
    }

    const response = await fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.error || 'Analysis failed');
    }

    return {
      success: true,
      data: result.result
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
 * Analyze file for AI content detection
 */
export const analyzeFile = async (file) => {
  try {
    if (!file) {
      return {
        success: false,
        error: 'Please provide a valid file to analyze.'
      };
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
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
 * Submit feedback for analysis results
 */
export const submitFeedback = async (feedback) => {
  if (!feedback || !feedback.type) {
    return {
      success: false,
      error: 'Feedback type is required'
    };
  }

  const response = await fetch(`${ANALYTICS_API_URL}/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(feedback)
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    return {
      success: false,
      error: errorData.error || `Feedback submission failed: ${response.status} ${response.statusText}`
    };
  }

  const data = await response.json();
  return {
    success: true,
    message: data.message || 'Feedback submitted successfully'
  };
};

/**
 * Track scan analytics
 */
export const trackScan = async (metadata = {}) => {
  try {
    const response = await fetch(`${ANALYTICS_API_URL}/track-scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        ...metadata
      })
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Tracking failed: ${response.status} ${response.statusText}`
      };
    }

    const data = await response.json();
    return {
      success: true,
      data: data
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Get user scan history
 */
export const getUserScans = async (userId) => {
  const response = await fetch(`${ANALYTICS_API_URL}/user-scans/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch user scans: ${response.status}`);
  }

  const data = await response.json();
  return {
    success: true,
    data: data.scans || []
  };
};

/**
 * Get available export formats
 */
export const getAvailableExportFormats = async () => {
  const response = await fetch(`${API_BASE_URL}/export/formats`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch export formats: ${response.status}`);
  }

  const data = await response.json();
  return {
    success: true,
    data: data.formats || ['pdf', 'json', 'csv']
  };
};

/**
 * Export analysis report
 */
export const exportReport = async (data, format = 'pdf') => {
  try {
    if (!data) {
      return {
        success: false,
        error: 'No data provided for export'
      };
    }

    if (!['pdf', 'json', 'csv'].includes(format)) {
      return {
        success: false,
        error: 'Invalid export format'
      };
    }

    const response = await fetch(`${API_BASE_URL}/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data,
        format
      })
    });

    if (!response.ok) {
      throw new Error(`Export request failed: ${response.status} ${response.statusText}`);
    }

    const contentDisposition = response.headers.get('content-disposition');
    let filename = `analysis-report.${format}`;
    
    if (contentDisposition && contentDisposition.includes('filename=')) {
      filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
    }
    
    const blob = await response.blob();
    
    return {
      success: true,
      blob: blob,
      filename: filename,
      format: format
    };
  } catch (error) {
    console.error('Error exporting report:', error);
    return {
      success: false,
      error: error.message || 'Failed to export report. Please try again.'
    };
  }
};