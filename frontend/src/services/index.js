/**
 * Services index - Re-exports all API modules for convenient imports
 *
 * This file provides backward compatibility by re-exporting all APIs from their modular files.
 * Components can now import from './services' or './services/index' instead of individual files.
 *
 * Usage:
 *   import { ordersAPI, productsAPI, authAPI } from './services';
 *   // or
 *   import { ordersAPI } from './services/orders-api';
 */

// Export base client utilities
export {
  API_BASE_URL,
  getToken,
  setToken,
  removeToken,
  getStoredUser,
  setStoredUser,
  authenticatedFetch,
  handleApiError
} from './api-client.js';

// Export authentication API
export { authAPI } from './auth-api.js';

// Export orders API
export { ordersAPI } from './orders-api.js';

// Export products API
export { productsAPI } from './products-api.js';

// Export clients API
export { clientsAPI } from './clients-api.js';

// Export shop, profile, and chats APIs
export { shopAPI, profileAPI, chatsAPI } from './shop-api.js';

// Export formatting utilities
export {
  formatDeliveryDate,
  formatOrderForDisplay,
  formatProductForDisplay,
  formatClientForDisplay
} from './formatters.js';
