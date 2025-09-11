module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.js'],
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },
  moduleNameMapper: {
    // CSS modules and CSS imports
    '^.+\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    // Static file imports (images, svgs, etc.)
    '^.+\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  testMatch: ['<rootDir>/tests/**/*.{test,spec}.{js,jsx}'],
  moduleFileExtensions: ['js', 'jsx'],
  // Increase default timeout for all tests to 30 seconds
  testTimeout: 30000,
};
