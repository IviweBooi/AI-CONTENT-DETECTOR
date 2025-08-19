import '@testing-library/jest-dom'

// Basic IntersectionObserver mock for jsdom
global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}
