import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';

/**
 * Custom render function that includes all necessary providers
 */
export function renderWithRouter(ui, { route = '/', ...renderOptions } = {}) {
  window.history.pushState({}, 'Test page', route);

  function Wrapper({ children }) {
    return (
      <MemoryRouter initialEntries={[route]}>
        {children}
      </MemoryRouter>
    );
  }

  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: Wrapper, ...renderOptions })
  };
}

/**
 * Simple render with user event setup
 */
export function renderWithUser(ui, options) {
  return {
    user: userEvent.setup(),
    ...render(ui, options)
  };
}

/**
 * Wait for async operations
 */
export const waitForLoadingToFinish = () =>
  new Promise(resolve => setTimeout(resolve, 0));

/**
 * Mock product data factory
 */
export const createMockProduct = (overrides = {}) => ({
  id: 1,
  name: 'Test Product',
  price: 1000,
  quantity: 10,
  image: '/test-image.jpg',
  category: 'Test Category',
  enabled: true,
  ...overrides
});

/**
 * Mock client data factory
 */
export const createMockClient = (overrides = {}) => ({
  id: 1,
  name: 'Test Client',
  phone: '+7 701 123 4567',
  totalOrders: 5,
  totalSum: 50000,
  lastOrder: '2024-01-01',
  ...overrides
});

/**
 * Custom queries for common patterns
 */
export const queries = {
  button: (name) => `button:has-text("${name}")`,
  input: (placeholder) => `input[placeholder="${placeholder}"]`,
  testId: (id) => `[data-testid="${id}"]`,
};