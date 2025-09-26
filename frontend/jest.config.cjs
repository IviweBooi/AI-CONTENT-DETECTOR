module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/config/setupTests.js'],
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },
  moduleNameMapper: {
    // CSS modules and CSS imports
    '^.+\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    // Static file imports (images, svgs, etc.)
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
    // Mock AuthContext to avoid import.meta issues
    '^../contexts/AuthContext$': '<rootDir>/__mocks__/AuthContext.js',
    '^../../src/contexts/AuthContext$': '<rootDir>/__mocks__/AuthContext.js',
    // Mock api.js to avoid import.meta issues
    '^../services/api$': '<rootDir>/__mocks__/api.js',
    '^../../src/services/api$': '<rootDir>/__mocks__/api.js',
  },
  testMatch: ['<rootDir>/tests/**/*.{test,spec}.{js,jsx}'],
  moduleFileExtensions: ['js', 'jsx'],
  // Increase default timeout for all tests to 30 seconds
  testTimeout: 30000,
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$))'
  ]
};
