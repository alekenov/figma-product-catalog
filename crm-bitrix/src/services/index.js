/**
 * Unified API exports for Bitrix CRM
 * Provides clean interface for all API operations
 */

export { ordersAPI } from './orders-api.js';
export { productsAPI } from './products-api.js';
export { bitrixFetch, buildQueryString } from './bitrix-client.js';
export { adaptOrder, adaptProduct, serializeProductForBitrix } from './bitrix-adapters.js';
export * from './formatters.js'; // Formatters re-export
