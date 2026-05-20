import '@testing-library/jest-dom';

// Mock fetch globally if needed
global.fetch = jest.fn();

// Reset fetch mock before each test
beforeEach(() => {
  global.fetch.mockClear();
});
