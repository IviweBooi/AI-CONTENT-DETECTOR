# Test Suite for AI Content Detector

This directory contains unit tests for the AI Content Detector frontend application using Jest and React Testing Library.

## Test Structure

The tests are organized into the following directories:

- `services/`: Tests for API service functions
- `components/`: Tests for React components
- `pages/`: Tests for page components
- `utils/`: Tests for utility functions

## Running Tests

You can run the tests using the following npm scripts:

```bash
# Run all tests
npm test

# Run tests in watch mode (for development)
npm run test:watch

# Run tests and generate dashboard data
npm run test:dashboard

# Run tests and serve the standalone dashboard
npm run test:dashboard:serve
```

## Test Dashboard

The application includes a visual test dashboard that displays test results and coverage information. You can use it in two ways:

### Option 1: Integrated with the main app

1. Run the tests with dashboard data generation:
   ```bash
   npm run test:dashboard
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Navigate to `/test-dashboard` in your browser to view the test results.

### Option 2: Standalone dashboard (for developers)

1. Run the tests and serve the standalone dashboard:
   ```bash
   npm run test:dashboard:serve
   ```
   This will automatically start a server and open the dashboard in your browser.

Alternatively, you can:
1. Run `npm run test:dashboard` to generate the test results
2. Open `frontend/test-results/index.html` directly in your browser

The dashboard provides:

- Summary of test results (passed, failed, skipped)
- Detailed test information by suite
- Code coverage metrics
- Ability to filter tests by status

## Writing New Tests

When adding new tests, follow these guidelines:

1. Place tests in the appropriate directory based on what you're testing
2. Name test files with `.test.js` or `.test.jsx` extension
3. Use descriptive test names that explain what's being tested
4. Mock external dependencies and API calls
5. Test both success and error scenarios

## Example Test Structure

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../src/components/MyComponent';

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  test('handles user interaction', () => {
    render(<MyComponent />);
    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('Result after click')).toBeInTheDocument();
  });
});
```