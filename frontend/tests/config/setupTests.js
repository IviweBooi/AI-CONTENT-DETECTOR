import '@testing-library/jest-dom'

// Mock import.meta for Jest
global.importMeta = {
  env: {
    VITE_API_BASE_URL: 'http://localhost:5000/api'
  }
}

// Add TextEncoder and TextDecoder polyfills for React Router compatibility
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Basic IntersectionObserver mock for jsdom
global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}
