import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ContentDetectPage from '../../src/pages/contentDetectPage';
import * as apiService from '../../src/services/api';

// Mock the API service
jest.mock('../../src/services/api', () => ({
  analyzeText: jest.fn(),
  analyzeFile: jest.fn(),
  submitFeedback: jest.fn(),
  trackScan: jest.fn(),
  exportReport: jest.fn().mockResolvedValue({
    success: true,
    blob: new Blob(['test'], { type: 'application/pdf' }),
    filename: 'test-report.pdf'
  }),
  getAvailableExportFormats: jest.fn().mockResolvedValue({
    success: true,
    data: { formats: ['pdf', 'json', 'csv'], default: 'pdf' }
  }),
  downloadBlob: jest.fn()
}));

// Mock SVG import
jest.mock('../../src/assets/icons/detect.svg', () => 'detect-icon.svg');

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('ContentDetectPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    
    // Setup default API responses
    apiService.analyzeText.mockResolvedValue({
      success: true,
      data: {
        aiLikelihood: 75,
        metricsBars: {
          structure: 80,
          vocabulary: 70,
          style: 75
        },
        text: 'Sample text for analysis'
      }
    });
    
    apiService.analyzeFile.mockResolvedValue({
      success: true,
      data: {
        aiLikelihood: 65,
        metricsBars: {
          structure: 60,
          vocabulary: 70,
          style: 65
        },
        text: 'Sample file content'
      }
    });
    
    apiService.submitFeedback.mockResolvedValue({
      success: true
    });
    
    apiService.trackScan.mockResolvedValue({
      success: true
    });
    
    apiService.exportReport.mockResolvedValue({
      success: true,
      data: {
        url: 'https://example.com/report.pdf',
        format: 'pdf'
      }
    });
  });

  test('renders the component with initial state', () => {
    render(<ContentDetectPage />);
    
    // Check for main elements
    expect(screen.getByText('AI Content Detector')).toBeInTheDocument();
    expect(screen.getByText('Text Input')).toBeInTheDocument();
    expect(screen.getByText('File Upload')).toBeInTheDocument();
    expect(screen.getByText('Analyze')).toBeInTheDocument();
    
    // Check for empty results panel
    expect(screen.getByText('Results will appear here after you analyze.')).toBeInTheDocument();
  });

  test('handles text input and character count', () => {
    render(<ContentDetectPage />);
    
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const testText = 'This is a test text for character counting';
    
    fireEvent.change(textarea, { target: { value: testText } });
    
    expect(textarea.value).toBe(testText);
    
    // Check character count display
    const characterCount = screen.getByText(new RegExp(`${testText.length}`));
    expect(characterCount).toBeInTheDocument();
  });

  test('disables analyze button when text is too short', () => {
    render(<ContentDetectPage />);
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    expect(analyzeButton).toBeDisabled();
    
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    fireEvent.change(textarea, { target: { value: 'Short text' } });
    
    expect(analyzeButton).toBeDisabled();
  });

  test('enables analyze button when text meets minimum length', async () => {
    render(<ContentDetectPage />);
    
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    
    // Generate text that meets minimum length (150 chars)
    const longText = 'A'.repeat(150);
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    expect(analyzeButton).not.toBeDisabled();
  });

  test('analyzes text and displays results', async () => {
    render(<ContentDetectPage />);
    
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const longText = 'A'.repeat(200) + ' This is a longer text that meets the minimum requirements for analysis.';
    
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    fireEvent.click(analyzeButton);
    
    // Wait for API call and results
    await waitFor(() => {
      expect(apiService.analyzeText).toHaveBeenCalledWith(longText);
    });
    
    // Check if results are displayed
    await waitFor(() => {
      expect(screen.getByText('Detection Results')).toBeInTheDocument();
    });
  });

  test('switches between text and file tabs', () => {
    render(<ContentDetectPage />);
    
    // Initially on text tab
    expect(screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...')).toBeVisible();
    
    // Switch to file tab
    const fileTabButton = screen.getByText('File Upload').closest('button');
    fireEvent.click(fileTabButton);
    
    // Check file upload area is visible
    expect(screen.getByText('Drop your file here')).toBeVisible();
    
    // Switch back to text tab
    const textTabButton = screen.getByText('Text Input').closest('button');
    fireEvent.click(textTabButton);
    
    // Check text area is visible again
    expect(screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...')).toBeVisible();
  });

  test('opens and submits feedback', async () => {
    // Clear previous mock calls
    apiService.submitFeedback.mockClear();
    
    // Mock successful feedback submission
    apiService.submitFeedback.mockResolvedValue({
      success: true,
      message: 'Feedback submitted successfully'
    });
    
    render(<ContentDetectPage />);
    
    // First analyze text to get results
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const longText = 'A'.repeat(500);
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    fireEvent.click(analyzeButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('Detection Results')).toBeInTheDocument();
    });
    
    // Click feedback button
    const feedbackButton = screen.getByText('Provide Feedback').closest('button');
    fireEvent.click(feedbackButton);
    
    // Wait for feedback modal to appear
    await waitFor(() => {
      expect(screen.getByText('Submit Feedback')).toBeInTheDocument();
    });
    
    // Select feedback type
    const accurateRadio = screen.getByLabelText('Accurate');
    fireEvent.click(accurateRadio);
    
    // Fill feedback form
    const feedbackTextarea = screen.getByPlaceholderText(/Please provide more details about your feedback/i);
    fireEvent.change(feedbackTextarea, { target: { value: 'This is test feedback' } });
    
    // Submit feedback
    const submitButton = screen.getByText('Submit Feedback').closest('button');
    fireEvent.click(submitButton);
    
    // Check API was called
    await waitFor(() => {
      expect(apiService.submitFeedback).toHaveBeenCalledWith(expect.objectContaining({
        type: 'Accurate',
        comment: 'This is test feedback'
      }));
    }, { timeout: 5000 });
  });

  test('exports report', async () => {
    render(<ContentDetectPage />);
    
    // First analyze text to get results
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const longText = 'A'.repeat(500);
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    fireEvent.click(analyzeButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('Detection Results')).toBeInTheDocument();
    });
    
    // Click export button to open dialog
    const exportButton = screen.getByText('Export Report').closest('button');
    fireEvent.click(exportButton);
    
    // Wait for export dialog to appear
    await waitFor(() => {
      expect(screen.getByText('Report Title')).toBeInTheDocument();
    });
    
    // Click the actual export confirmation button
    const confirmExportButton = screen.getByText(/Export as PDF/i).closest('button');
    fireEvent.click(confirmExportButton);
    
    // Check API was called
    await waitFor(() => {
      expect(apiService.exportReport).toHaveBeenCalled();
    });
  });

  test('handles file upload', async () => {
    // Mock successful file analysis
    apiService.analyzeFile.mockResolvedValue({
      success: true,
      data: { text: 'This is the extracted file content.' }
    });
    
    render(<ContentDetectPage />);
    
    // Switch to file tab
    const fileTabButton = screen.getByText('File Upload').closest('button');
    fireEvent.click(fileTabButton);
    
    // Create a mock file
    const file = new File(['test file content'], 'test.txt', { type: 'text/plain' });
    
    // Find file input and upload file
    const fileInput = document.getElementById('file-input');
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Click analyze button
    const analyzeButton = document.querySelector('.analyze-button');
    fireEvent.click(analyzeButton);
    
    // Wait for API call
    await waitFor(() => {
      expect(apiService.analyzeFile).toHaveBeenCalledWith(file, null);
    });
  });

  test('displays error when API call fails', async () => {
    // Mock API to return error
    apiService.analyzeText.mockRejectedValueOnce(new Error('API Error'));
    
    render(<ContentDetectPage />);
    
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const longText = 'A'.repeat(200);
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    fireEvent.click(analyzeButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  test('shows loading state during analysis', async () => {
    // Mock API to take some time
    apiService.analyzeText.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(<ContentDetectPage />);
    
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const longText = 'A'.repeat(200);
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    fireEvent.click(analyzeButton);
    
    // Check loading state
    expect(screen.getByText('Analyzing…')).toBeInTheDocument();
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText('Analyzing…')).not.toBeInTheDocument();
    });
  });
});