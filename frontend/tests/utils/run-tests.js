/**
 * Test Runner Script
 * 
 * This script runs Jest tests and generates a JSON report that can be used by the Test Dashboard.
 * It uses Jest's programmatic API to run tests and collect results.
 * 
 * This script can be run independently to generate test results for the standalone dashboard.
 */

import { runCLI } from '@jest/core';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../../'); // Go up to frontend root

// Configuration for Jest
const jestConfig = {
  // Use the same configuration as in jest.config.cjs
  projects: [projectRoot],
  json: true,
  outputFile: path.join(__dirname, '../reports/test-results.json'),
  collectCoverage: true,
  coverageDirectory: path.join(__dirname, '../reports/coverage'),
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)', 'tests/**/*.[jt]s?(x)'],
};

// Run Jest tests
runCLI(jestConfig, [projectRoot])
  .then(({ results }) => {
    // Format the results for the dashboard
    const formattedResults = {
      summary: {
        total: results.numTotalTests,
        passed: results.numPassedTests,
        failed: results.numFailedTests,
        skipped: results.numPendingTests,
        duration: results.startTime ? (Date.now() - results.startTime) / 1000 : 0,
        coverage: results.coverageMap ? calculateOverallCoverage(results.coverageMap) : null,
        lastRun: new Date().toISOString(),
      },
      suites: formatTestSuites(results.testResults),
    };

    // Create output directory if it doesn't exist
    const outputDir = path.join(__dirname, '../reports/test-results');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Write the formatted results to a file that can be loaded by the dashboard
    const resultsPath = path.join(outputDir, 'test-dashboard-data.json');
    fs.writeFileSync(resultsPath, JSON.stringify(formattedResults, null, 2));
    
    // Also copy to public directory for the main app if it exists
    const publicDir = path.join(projectRoot, 'public');
    if (fs.existsSync(publicDir)) {
      fs.writeFileSync(
        path.join(publicDir, 'test-dashboard-data.json'),
        JSON.stringify(formattedResults, null, 2)
      );
    }
    
    // Copy the standalone dashboard HTML file to the output directory
    const dashboardHtmlPath = path.join(__dirname, '../reports/test-dashboard.html');
    if (fs.existsSync(dashboardHtmlPath)) {
      fs.copyFileSync(dashboardHtmlPath, path.join(outputDir, 'index.html'));
    }
    
    console.log('Test results processed and saved for the dashboard.');
    console.log(`Standalone dashboard available at: ${path.join(outputDir, 'index.html')}`);
    console.log('You can open this file directly in your browser to view the test results.');
    
    // Exit with appropriate code
    process.exit(results.success ? 0 : 1);
  })
  .catch(error => {
    console.error('Error running tests:', error);
    process.exit(1);
  });

/**
 * Calculate overall coverage percentage from coverage map
 */
function calculateOverallCoverage(coverageMap) {
  if (!coverageMap || typeof coverageMap.getCoverageSummary !== 'function') {
    return null;
  }
  
  const summary = coverageMap.getCoverageSummary();
  if (!summary) return null;
  
  const { covered, total } = summary.lines || { covered: 0, total: 0 };
  return total > 0 ? (covered / total) * 100 : 0;
}

/**
 * Format test results into a structure suitable for the dashboard
 */
function formatTestSuites(testResults) {
  const suites = [];
  
  // Group by file path to create logical suites
  const suiteGroups = {};
  
  testResults.forEach(result => {
    const filePath = result.testFilePath;
    const relativePath = path.relative(__dirname, filePath);
    
    // Determine suite type based on file path
    let suiteType = 'Other Tests';
    if (relativePath.includes('services')) {
      suiteType = 'API Service Tests';
    } else if (relativePath.includes('components')) {
      suiteType = 'Component Tests';
    } else if (relativePath.includes('pages')) {
      suiteType = 'Page Tests';
    } else if (relativePath.includes('utils')) {
      suiteType = 'Utility Tests';
    }
    
    // Initialize suite group if it doesn't exist
    if (!suiteGroups[suiteType]) {
      suiteGroups[suiteType] = {
        name: suiteType,
        passed: 0,
        failed: 0,
        skipped: 0,
        duration: 0,
        suites: [],
      };
    }
    
    // Extract file name for the sub-suite name
    const fileName = path.basename(filePath);
    
    // Create sub-suite for this test file
    const subSuite = {
      name: fileName,
      tests: [],
    };
    
    // Process test results
    result.testResults.forEach(testResult => {
      const status = testResult.status === 'passed' ? 'passed' : 
                    testResult.status === 'failed' ? 'failed' : 'skipped';
      
      // Update suite counters
      if (status === 'passed') suiteGroups[suiteType].passed++;
      else if (status === 'failed') suiteGroups[suiteType].failed++;
      else suiteGroups[suiteType].skipped++;
      
      // Add test details
      subSuite.tests.push({
        name: testResult.title,
        status,
        duration: testResult.duration / 1000, // Convert to seconds
        error: status === 'failed' ? formatError(testResult) : null,
      });
    });
    
    // Add duration
    suiteGroups[suiteType].duration += result.perfStats.end - result.perfStats.start;
    
    // Add sub-suite to the suite group
    suiteGroups[suiteType].suites.push(subSuite);
  });
  
  // Convert suite groups to array
  Object.values(suiteGroups).forEach(group => {
    // Convert duration to seconds
    group.duration = group.duration / 1000;
    suites.push(group);
  });
  
  return suites;
}

/**
 * Format error message from test result
 */
function formatError(testResult) {
  if (!testResult.failureMessages || testResult.failureMessages.length === 0) {
    return 'Unknown error';
  }
  
  // Extract the main error message without the stack trace
  const fullMessage = testResult.failureMessages[0];
  const errorMatch = fullMessage.match(/Error: (.+?)(?:\n|$)/);
  return errorMatch ? errorMatch[1] : fullMessage.split('\n')[0];
}