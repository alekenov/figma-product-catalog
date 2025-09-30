/**
 * Price utilities for converting between kopecks (backend) and tenge (frontend)
 *
 * Backend stores prices in kopecks (1 tenge = 100 kopecks)
 * Frontend displays prices in tenge with proper formatting
 */

/**
 * Convert kopecks to tenge
 * @param {number} kopecks - Price in kopecks
 * @returns {number} - Price in tenge
 */
export const kopecksToTenge = (kopecks) => {
  return Math.round(kopecks / 100);
};

/**
 * Convert tenge to kopecks
 * @param {number} tenge - Price in tenge
 * @returns {number} - Price in kopecks
 */
export const tengeToKopecks = (tenge) => {
  return Math.round(tenge * 100);
};

/**
 * Format price for display with tenge symbol
 * @param {number} kopecks - Price in kopecks
 * @param {boolean} includeSymbol - Whether to include ₸ symbol
 * @returns {string} - Formatted price (e.g., "12 000 ₸")
 */
export const formatPrice = (kopecks, includeSymbol = true) => {
  const tenge = kopecksToTenge(kopecks);
  const formatted = tenge.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return includeSymbol ? `${formatted} ₸` : formatted;
};

/**
 * Parse price string to kopecks
 * @param {string} priceStr - Price string (e.g., "12 000 ₸" or "12000")
 * @returns {number} - Price in kopecks
 */
export const parsePrice = (priceStr) => {
  // Remove all non-digit characters
  const cleanStr = priceStr.replace(/[^\d]/g, '');
  const tenge = parseInt(cleanStr, 10) || 0;
  return tengeToKopecks(tenge);
};

/**
 * Calculate delivery cost based on subtotal
 * @param {number} subtotalKopecks - Subtotal in kopecks
 * @param {number} deliveryCostKopecks - Standard delivery cost in kopecks
 * @param {number} freeDeliveryThresholdKopecks - Free delivery threshold in kopecks
 * @returns {number} - Delivery cost in kopecks (0 if free)
 */
export const calculateDeliveryCost = (
  subtotalKopecks,
  deliveryCostKopecks = 150000, // 1500 tenge default
  freeDeliveryThresholdKopecks = 1500000 // 15000 tenge default
) => {
  return subtotalKopecks >= freeDeliveryThresholdKopecks ? 0 : deliveryCostKopecks;
};