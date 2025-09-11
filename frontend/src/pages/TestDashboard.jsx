import { useState, useEffect } from 'react';
import '../styles/TestDashboard.css';

export default function TestDashboard() {
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    // Attempt to load real test results if available, otherwise use mock data
    setLoading(true);
    
    // Try to fetch the test results JSON file
    fetch('/test-dashboard-data.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Test results not found');
        }
        return response.json();
      })
      .then(data => {
        setTestResults(data);
        setLoading(false);
      })
      .catch(err => {
        console.log('Using mock data:', err.message);
        // Fall back to mock data if the file doesn't exist
        const mockResults = generateMockTestResults();
        setTestResults(mockResults);
        setLoading(false);
      });
  }, []);

  // Generate mock test results for demonstration
  function generateMockTestResults() {
    const apiTests = {
      name: 'API Service Tests',
      passed: 14,
      failed: 1,
      skipped: 0,
      duration: 1.23,
      suites: [
        {
          name: 'analyzeText',
          tests: [
            { name: 'should return a successful response with simulated data', status: 'passed', duration: 0.12 },
            { name: 'should handle empty text input', status: 'passed', duration: 0.05 },
            { name: 'should simulate network delay', status: 'passed', duration: 0.21 }
          ]
        },
        {
          name: 'analyzeFile',
          tests: [
            { name: 'should return a successful response with simulated data for a text file', status: 'passed', duration: 0.15 },
            { name: 'should handle null file input', status: 'passed', duration: 0.04 }
          ]
        },
        {
          name: 'submitFeedback',
          tests: [
            { name: 'should return a successful response for valid feedback', status: 'passed', duration: 0.08 },
            { name: 'should handle missing feedback type', status: 'passed', duration: 0.06 }
          ]
        },
        {
          name: 'trackScan',
          tests: [
            { name: 'should return a successful response for tracking with metadata', status: 'passed', duration: 0.07 },
            { name: 'should return a successful response for tracking without metadata', status: 'passed', duration: 0.05 }
          ]
        },
        {
          name: 'exportReport',
          tests: [
            { name: 'should return a successful response for PDF export', status: 'passed', duration: 0.11 },
            { name: 'should handle missing result data', status: 'passed', duration: 0.06 },
            { name: 'should support different export formats', status: 'failed', duration: 0.09, 
              error: 'Expected property "format" to equal "csv" but received "pdf"' }
          ]
        }
      ]
    };
    
    const componentTests = {
      name: 'Component Tests',
      passed: 7,
      failed: 0,
      skipped: 0,
      duration: 2.45,
      suites: [
        {
          name: 'ContentDetectPage Component',
          tests: [
            { name: 'renders the component with initial state', status: 'passed', duration: 0.35 },
            { name: 'handles text input and character count', status: 'passed', duration: 0.28 },
            { name: 'disables analyze button when text is too short', status: 'passed', duration: 0.31 },
            { name: 'enables analyze button when text meets minimum length', status: 'passed', duration: 0.42 },
            { name: 'analyzes text and displays results', status: 'passed', duration: 0.52 },
            { name: 'switches between text and file tabs', status: 'passed', duration: 0.27 },
            { name: 'opens and submits feedback', status: 'passed', duration: 0.30 }
          ]
        }
      ]
    };
    
    return {
      summary: {
        total: apiTests.passed + apiTests.failed + apiTests.skipped + 
               componentTests.passed + componentTests.failed + componentTests.skipped,
        passed: apiTests.passed + componentTests.passed,
        failed: apiTests.failed + componentTests.failed,
        skipped: apiTests.skipped + componentTests.skipped,
        duration: apiTests.duration + componentTests.duration,
        coverage: 87.5, // Mock coverage percentage
        lastRun: new Date().toISOString()
      },
      suites: [apiTests, componentTests]
    };
  }

  // Filter tests based on status
  function getFilteredTests(suite) {
    if (filter === 'all') return suite.tests;
    return suite.tests.filter(test => test.status === filter);
  }

  // Render loading state
  if (loading) {
    return (
      <div className="test-dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading test results...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="test-dashboard">
        <div className="error-container">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="test-dashboard">
      <div className="dashboard-header">
        <h1>Test Results Dashboard</h1>
        <div className="dashboard-actions">
          <button className="refresh-btn" onClick={() => window.location.reload()}>
            <i className="fa-solid fa-sync-alt"></i> Refresh
          </button>
          <button className="run-tests-btn">
            <i className="fa-solid fa-play"></i> Run Tests
          </button>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={`tab-btn ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Test Details
        </button>
        <button 
          className={`tab-btn ${activeTab === 'coverage' ? 'active' : ''}`}
          onClick={() => setActiveTab('coverage')}
        >
          Coverage
        </button>
      </div>

      {activeTab === 'summary' && (
        <div className="summary-tab">
          <div className="summary-cards">
            <div className="summary-card total">
              <h3>Total Tests</h3>
              <div className="card-value">{testResults.summary.total}</div>
            </div>
            <div className="summary-card passed">
              <h3>Passed</h3>
              <div className="card-value">{testResults.summary.passed}</div>
            </div>
            <div className="summary-card failed">
              <h3>Failed</h3>
              <div className="card-value">{testResults.summary.failed}</div>
            </div>
            <div className="summary-card skipped">
              <h3>Skipped</h3>
              <div className="card-value">{testResults.summary.skipped}</div>
            </div>
          </div>

          <div className="summary-details">
            <div className="summary-item">
              <span className="label">Duration:</span>
              <span className="value">{testResults.summary.duration.toFixed(2)}s</span>
            </div>
            <div className="summary-item">
              <span className="label">Last Run:</span>
              <span className="value">{new Date(testResults.summary.lastRun).toLocaleString()}</span>
            </div>
            <div className="summary-item">
              <span className="label">Coverage:</span>
              <span className="value">{testResults.summary.coverage}%</span>
            </div>
          </div>

          <div className="test-suites-summary">
            <h3>Test Suites</h3>
            {testResults.suites.map((suite, index) => (
              <div key={index} className="suite-summary">
                <h4>{suite.name}</h4>
                <div className="suite-stats">
                  <div className="stat">
                    <span className="label">Passed:</span>
                    <span className="value passed">{suite.passed}</span>
                  </div>
                  <div className="stat">
                    <span className="label">Failed:</span>
                    <span className="value failed">{suite.failed}</span>
                  </div>
                  <div className="stat">
                    <span className="label">Duration:</span>
                    <span className="value">{suite.duration.toFixed(2)}s</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'details' && (
        <div className="details-tab">
          <div className="filter-controls">
            <span>Filter:</span>
            <div className="filter-buttons">
              <button 
                className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                onClick={() => setFilter('all')}
              >
                All
              </button>
              <button 
                className={`filter-btn ${filter === 'passed' ? 'active' : ''}`}
                onClick={() => setFilter('passed')}
              >
                Passed
              </button>
              <button 
                className={`filter-btn ${filter === 'failed' ? 'active' : ''}`}
                onClick={() => setFilter('failed')}
              >
                Failed
              </button>
              <button 
                className={`filter-btn ${filter === 'skipped' ? 'active' : ''}`}
                onClick={() => setFilter('skipped')}
              >
                Skipped
              </button>
            </div>
          </div>

          <div className="test-details">
            {testResults.suites.map((suite, suiteIndex) => (
              <div key={suiteIndex} className="test-suite">
                <h3 className="suite-name">{suite.name}</h3>
                
                {suite.suites.map((subSuite, subSuiteIndex) => (
                  <div key={subSuiteIndex} className="sub-suite">
                    <h4 className="sub-suite-name">{subSuite.name}</h4>
                    
                    <table className="tests-table">
                      <thead>
                        <tr>
                          <th>Test</th>
                          <th>Status</th>
                          <th>Duration</th>
                        </tr>
                      </thead>
                      <tbody>
                        {getFilteredTests(subSuite).map((test, testIndex) => (
                          <tr key={testIndex} className={`test-row ${test.status}`}>
                            <td className="test-name">{test.name}</td>
                            <td className="test-status">
                              <span className={`status-badge ${test.status}`}>
                                {test.status}
                              </span>
                            </td>
                            <td className="test-duration">{test.duration.toFixed(2)}s</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    
                    {subSuite.tests.some(test => test.status === 'failed') && (
                      <div className="failed-tests">
                        {subSuite.tests
                          .filter(test => test.status === 'failed')
                          .map((test, index) => (
                            <div key={index} className="error-details">
                              <h5>Error in: {test.name}</h5>
                              <pre className="error-message">{test.error}</pre>
                            </div>
                          ))
                        }
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'coverage' && (
        <div className="coverage-tab">
          <div className="coverage-summary">
            <div className="coverage-chart">
              <div 
                className="coverage-fill" 
                style={{ width: `${testResults.summary.coverage}%` }}
              ></div>
              <span className="coverage-percentage">{testResults.summary.coverage}%</span>
            </div>
            <p className="coverage-description">
              Code coverage represents the percentage of your codebase that is covered by tests.
              Higher coverage generally indicates better test quality.  
            </p>
          </div>

          <div className="coverage-files">
            <h3>Coverage by File</h3>
            <table className="coverage-table">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Statements</th>
                  <th>Branches</th>
                  <th>Functions</th>
                  <th>Lines</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>src/services/api.js</td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '95%' }}></div>
                      <span>95%</span>
                    </div>
                  </td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '85%' }}></div>
                      <span>85%</span>
                    </div>
                  </td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '100%' }}></div>
                      <span>100%</span>
                    </div>
                  </td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '92%' }}></div>
                      <span>92%</span>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>src/pages/contentDetectPage.jsx</td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '82%' }}></div>
                      <span>82%</span>
                    </div>
                  </td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '75%' }}></div>
                      <span>75%</span>
                    </div>
                  </td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '90%' }}></div>
                      <span>90%</span>
                    </div>
                  </td>
                  <td>
                    <div className="coverage-bar">
                      <div className="bar-fill" style={{ width: '85%' }}></div>
                      <span>85%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}