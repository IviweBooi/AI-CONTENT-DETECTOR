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
  exportReport: jest.fn()
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
    
    // Enter text
    fireEvent.change(textarea, { target: { value: 'Sample text for testing' } });
    
    // Check character count
    expect(screen.getByText(/characters/)).toHaveTextContent('23 / 2,000 characters');
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
    
    // Generate text that meets minimum length (500 chars)
    const longText = 'A'.repeat(500);
    fireEvent.change(textarea, { target: { value: longText } });
    
    const analyzeButton = screen.getByText('Analyze').closest('button');
    expect(analyzeButton).not.toBeDisabled();
  });

  test('analyzes text and displays results', async () => {
    render(<ContentDetectPage />);
    
    // Enter text that meets minimum length
    const textarea = screen.getByPlaceholderText('Paste or type your content here for AI detection analysis...');
    const longText = 'A'.repeat(500);
    fireEvent.change(textarea, { target: { value: longText } });
    
    // Click analyze button
    const analyzeButton = screen.getByText('Analyze').closest('button');
    fireEvent.click(analyzeButton);
    
    // Wait for results
    await waitFor(() => {
      expect(apiService.analyzeText).toHaveBeenCalledWith(longText);
      expect(screen.getByText('Detection Results')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument(); // AI likelihood
      expect(screen.getByText('Likely AI‑generated')).toBeInTheDocument();
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
    
    // Open feedback modal
    const feedbackButton = screen.getByText('Provide Feedback').closest('button');
    fireEvent.click(feedbackButton);
    
    // Check modal is open
    expect(screen.getByText('How accurate was the content detection?')).toBeInTheDocument();
    
    // Select feedback type
    const accurateOption = screen.getByLabelText('Accurate');
    fireEvent.click(accurateOption);
    
    // Add comment
    const commentTextarea = screen.getByPlaceholderText('Please provide more details about your feedback...');
    fireEvent.change(commentTextarea, { target: { value: 'This is a test comment' } });
    
    // Submit feedback
    const submitButton = screen.getByText('Submit Feedback');
    fireEvent.click(submitButton);
    
    // Check API was called
    await waitFor(() => {
      expect(apiService.submitFeedback).toHaveBeenCalledWith({
        type: 'Accurate',
        comment: 'This is a test comment',
        resultId: expect.any(String)
      });
    });
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
    
    // Click export button
    const exportButton = screen.getByText('Export Report').closest('button');
    fireEvent.click(exportButton);
    
    // Check API was called
    await waitFor(() => {
      expect(apiService.exportReport).toHaveBeenCalled();
    });
  });
});