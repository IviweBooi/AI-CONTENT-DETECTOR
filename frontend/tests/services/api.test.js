import { analyzeText, analyzeFile, submitFeedback, trackScan, exportReport } from '../../src/services/api';

// Mock global fetch
global.fetch = jest.fn();

// Mock process.env for testing
process.env.NODE_ENV = 'test';

// Mock performance.now for consistent timing tests
const originalPerformanceNow = global.performance.now;
global.performance.now = jest.fn().mockReturnValue(100);

// Mock File object for file tests
class MockFile extends Blob {
  constructor(data, fileName, options) {
    super(data, options);
    this.name = fileName;
    this.lastModified = new Date();
  }
}

// Mock window.URL for blob tests
global.URL = {
  createObjectURL: jest.fn(() => 'mock-url'),
  revokeObjectURL: jest.fn()
};

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  afterAll(() => {
    global.performance.now = originalPerformanceNow;
  });

  describe('analyzeText', () => {
    it('should return a successful response with mocked backend data', async () => {
      const mockResponse = {
        success: true,
        result: {
          ai_probability: 0.75,
          metricsBars: {
            structure: 80,
            vocabulary: 70,
            style: 75
          }
        }
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const text = 'This is a sample text for analysis';
      const result = await analyzeText(text);

      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('data');
      expect(result.data).toHaveProperty('ai_probability');
      expect(result.data).toHaveProperty('metricsBars');
      expect(result.data.metricsBars).toHaveProperty('structure');
      expect(result.data.metricsBars).toHaveProperty('vocabulary');
      expect(result.data.metricsBars).toHaveProperty('style');
    });

    it('should handle empty text input', async () => {
      const result = await analyzeText('');

      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: 'Invalid request' })
      });

      const text = 'Sample text for analysis';
      const result = await analyzeText(text);
      
      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });
  });

  describe('analyzeFile', () => {
    it('should analyze file successfully', async () => {
      const mockResponse = {
        success: true,
        content: 'test content from file',
        result: {
          ai_probability: 0.85,
          metricsBars: [
            { name: 'AI Probability', value: 85 },
            { name: 'Human Probability', value: 15 }
          ]
        }
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const result = await analyzeFile(file);

      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('data');
      expect(result.data).toHaveProperty('text');
      expect(result.data).toHaveProperty('result');
      expect(result.data).toHaveProperty('fileInfo');
      expect(result.data.fileInfo).toHaveProperty('name');
      expect(result.data.fileInfo).toHaveProperty('size');
    });

    it('should handle null file input', async () => {
      const result = await analyzeFile(null);

      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });

    it('should handle file upload errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: 'Invalid file' })
      });

      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const result = await analyzeFile(file);
      
      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });
  });

  describe('submitFeedback', () => {
    it('should return a successful response for valid feedback', async () => {
      const mockResponse = {
        status: 'success',
        message: 'Feedback submitted successfully'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const feedback = {
        type: 'Accurate',
        comment: 'This is a test comment',
        resultId: 'test-123'
      };
      
      const result = await submitFeedback(feedback);

      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('message');
    });

    it('should handle missing feedback type', async () => {
      const feedback = {
        comment: 'This is a test comment',
        resultId: 'test-123'
      };
      
      const result = await submitFeedback(feedback);

      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' })
      });

      const feedbackData = {
        type: 'Accurate',
        comment: 'This is a test comment',
        resultId: 'test-123'
      };
      
      const result = await submitFeedback(feedbackData);
      
      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });
  });

  describe('trackScan', () => {
    it('should return a successful response for tracking with metadata', async () => {
      const mockResponse = {
        success: true,
        message: 'Scan tracked successfully'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const metadata = {
        contentType: 'text',
        contentLength: 100
      };
      
      const result = await trackScan(metadata);

      expect(result).toHaveProperty('success', true);
    });

    it('should return a successful response for tracking without metadata', async () => {
      const mockResponse = {
        success: true,
        message: 'Scan tracked successfully'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await trackScan();

      expect(result).toHaveProperty('success', true);
    });

    it('should handle API errors gracefully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' })
      });

      const metadata = {
        contentType: 'text',
        contentLength: 100
      };
      
      const result = await trackScan(metadata);

      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });
  });

  describe('exportReport', () => {
    it('should return a successful response for PDF export', async () => {
      const mockBlob = new Blob(['mock pdf content'], { type: 'application/pdf' });
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        headers: {
          get: (name) => name === 'content-disposition' ? 'attachment; filename="report.pdf"' : null
        },
        blob: async () => mockBlob
      });

      const data = {
        text: 'Sample text',
        ai_probability: 0.8,
        metricsBars: [
          { label: 'Metric 1', value: 0.7 },
          { label: 'Metric 2', value: 0.9 }
        ]
      };
      
      const result = await exportReport(data, 'pdf');

      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('blob');
      expect(result).toHaveProperty('filename');
      expect(result).toHaveProperty('format', 'pdf');
    });

    it('should handle missing data', async () => {
      const result = await exportReport(null, 'pdf');

      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });

    it('should support different formats', async () => {
      const mockBlob = new Blob(['mock content'], { type: 'text/csv' });
      
      global.fetch.mockResolvedValue({
        ok: true,
        headers: {
          get: (name) => name === 'content-disposition' ? 'attachment; filename="report.csv"' : null
        },
        blob: async () => mockBlob
      });

      const data = {
        text: 'Sample text',
        ai_probability: 0.8,
        metricsBars: [
          { label: 'Metric 1', value: 0.7 },
          { label: 'Metric 2', value: 0.9 }
        ]
      };
      
      const csvResult = await exportReport(data, 'csv');
      expect(csvResult).toHaveProperty('success', true);
      expect(csvResult).toHaveProperty('blob');
      expect(csvResult).toHaveProperty('format', 'csv');

      const jsonResult = await exportReport(data, 'json');
      expect(jsonResult).toHaveProperty('success', true);
      expect(jsonResult).toHaveProperty('blob');
      expect(jsonResult).toHaveProperty('format', 'json');
    });

    it('should handle API errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' })
      });

      const reportData = {
        text: 'Sample text',
        result: 'ai',
        confidence: 0.85
      };
      
      const result = await exportReport(reportData, 'pdf');
      
      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });
  });
});