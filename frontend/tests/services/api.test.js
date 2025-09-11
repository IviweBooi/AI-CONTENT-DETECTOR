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
    it('should return a successful response with simulated data', async () => {
      const text = 'This is a sample text for analysis';
      const result = await analyzeText(text);

      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('data');
      expect(result.data).toHaveProperty('aiLikelihood');
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

    it('should simulate network delay', async () => {
      const text = 'This is a sample text for analysis';
      const startTime = Date.now();
      
      const promise = analyzeText(text);
      jest.advanceTimersByTime(1000); // Advance timers to simulate delay
      const result = await promise;
      
      expect(result).toHaveProperty('success', true);
    });
  });

  describe('analyzeFile', () => {
    it('should return a successful response with simulated data for a text file', async () => {
      const file = new MockFile(['file content'], 'test.txt', { type: 'text/plain' });
      const result = await analyzeFile(file);

      expect(result).toHaveProperty('success', true);
      expect(result).toHaveProperty('data');
      expect(result.data).toHaveProperty('aiLikelihood');
      expect(result.data).toHaveProperty('text');
    }, 10000); // Increase timeout to 10 seconds

    it('should handle null file input', async () => {
      const result = await analyzeFile(null);

      expect(result).toHaveProperty('success', false);
      expect(result).toHaveProperty('error');
    });
  });

  describe('submitFeedback', () => {
    it('should return a successful response for valid feedback', async () => {
      const feedback = {
        type: 'Accurate',
        comment: 'This is a test comment',
        resultId: 'test-123'
      };
      
      const result = await submitFeedback(feedback);

      expect(result).toHaveProperty('success', true);
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
  });

  describe('trackScan', () => {
    it('should return a successful response for tracking with metadata', async () => {
      const metadata = {
        contentType: 'text',
        contentLength: 100
      };
      
      const result = await trackScan(metadata);

      expect(result).toHaveProperty('success', true);
    });

    it('should return a successful response for tracking without metadata', async () => {
      const result = await trackScan();

      expect(result).toHaveProperty('success', true);
    });
  });

  describe('exportReport', () => {
    it('should return a successful response for PDF export', async () => {
      const result = {
        aiLikelihood: 75,
        metricsBars: {
          structure: 80,
          vocabulary: 70,
          style: 75
        },
        text: 'Sample text for export'
      };
      
      const exportResult = await exportReport(result, 'pdf');

      expect(exportResult).toHaveProperty('success', true);
      expect(exportResult).toHaveProperty('data');
      expect(exportResult.data).toHaveProperty('url');
    }, 10000); // Increase timeout to 10 seconds

    it('should handle missing result data', async () => {
      const exportResult = await exportReport(null, 'pdf');

      expect(exportResult).toHaveProperty('success', false);
      expect(exportResult).toHaveProperty('error');
    }, 10000); // Increase timeout to 10 seconds

    it('should support different export formats', async () => {
      const result = {
        aiLikelihood: 75,
        metricsBars: {
          structure: 80,
          vocabulary: 70,
          style: 75
        },
        text: 'Sample text for export'
      };
      
      const exportResult = await exportReport(result, 'csv');

      expect(exportResult).toHaveProperty('success', true);
      expect(exportResult.data).toHaveProperty('format', 'csv');
    }, 10000); // Increase timeout to 10 seconds
  });
});