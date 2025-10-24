/**
 * API Response Validator
 * Validates API responses against expected structure and logs warnings
 * Helps catch API changes early in development
 */

const VALIDATION_ENABLED = import.meta.env.DEV; // Only in development

/**
 * Type checkers
 */
const isString = (val) => typeof val === 'string';
const isNumber = (val) => typeof val === 'number';
const isBoolean = (val) => typeof val === 'boolean';
const isArray = (val) => Array.isArray(val);
const isObject = (val) => val !== null && typeof val === 'object' && !Array.isArray(val);
const isNullable = (val, checker) => val === null || val === undefined || checker(val);

/**
 * Schema definitions for API responses
 */
const schemas = {
  orderListItem: {
    id: isNumber,
    status: isString,
    status_name: isString,
    recipient: {
      name: (val) => isNullable(val, isString),
      phone: (val) => isNullable(val, isString),
    },
    deliveryTime: (val) => isNullable(val, isString),
    deliveryMethod: (val) => isNullable(val, isString),
    deliveryAddress: (val) => isNullable(val, isString),
    mainImage: (val) => isNullable(val, isString),
    itemImages: isArray,
    paymentAmount: (val) => isNullable(val, isString),
    executors: isArray,
    createdAt: (val) => isNullable(val, isString),
  },

  orderListResponse: {
    success: isBoolean,
    data: isArray,
    pagination: (val) => {
      if (!isObject(val)) return false;
      return (
        isNumber(val.total) &&
        isNumber(val.limit) &&
        isNumber(val.offset) &&
        isBoolean(val.hasMore)
      );
    },
  },
};

/**
 * Validate value against schema
 * @param {any} value - Value to validate
 * @param {Object|Function} schema - Schema definition
 * @param {string} path - Current path in object (for error messages)
 * @returns {string[]} Array of validation errors
 */
function validateValue(value, schema, path = 'root') {
  const errors = [];

  // If schema is a function, use it directly
  if (typeof schema === 'function') {
    if (!schema(value)) {
      errors.push(`${path}: Type mismatch (got ${typeof value}, value: ${JSON.stringify(value)})`);
    }
    return errors;
  }

  // If schema is an object, validate recursively
  if (isObject(schema)) {
    if (!isObject(value) && value !== null && value !== undefined) {
      errors.push(`${path}: Expected object, got ${typeof value}`);
      return errors;
    }

    if (value === null || value === undefined) {
      errors.push(`${path}: Expected object, got ${value}`);
      return errors;
    }

    // Check for missing required fields
    for (const key in schema) {
      if (!(key in value)) {
        errors.push(`${path}.${key}: Missing field`);
      } else {
        errors.push(...validateValue(value[key], schema[key], `${path}.${key}`));
      }
    }

    // Check for unexpected fields (warn only)
    for (const key in value) {
      if (!(key in schema) && key !== '_debug') {
        console.warn(`${path}.${key}: Unexpected field (not in schema)`);
      }
    }
  }

  return errors;
}

/**
 * Validate order list response
 * @param {Object} response - API response
 * @returns {boolean} True if valid
 */
export function validateOrderListResponse(response) {
  if (!VALIDATION_ENABLED) return true;

  const errors = validateValue(response, schemas.orderListResponse);

  if (errors.length > 0) {
    console.group('❌ API Validation Failed: Order List Response');
    errors.forEach((error) => console.error(error));
    console.groupEnd();
    return false;
  }

  // Validate each order item
  if (response.success && Array.isArray(response.data)) {
    let itemErrors = [];
    response.data.forEach((item, index) => {
      const itemValidation = validateValue(item, schemas.orderListItem, `data[${index}]`);
      itemErrors.push(...itemValidation);
    });

    if (itemErrors.length > 0) {
      console.group('⚠️ API Validation Warnings: Order List Items');
      itemErrors.forEach((error) => console.warn(error));
      console.groupEnd();
    }
  }

  console.log('✅ API Validation Passed: Order List Response');
  return true;
}

/**
 * Validate single order detail response
 * @param {Object} response - API response
 * @returns {boolean} True if valid
 */
export function validateOrderDetailResponse(response) {
  if (!VALIDATION_ENABLED) return true;

  const errors = [];

  if (!isObject(response)) {
    console.error('❌ API Validation Failed: Response is not an object');
    return false;
  }

  if (!isBoolean(response.success)) {
    errors.push('success: Expected boolean');
  }

  if (response.success && response.data) {
    const dataErrors = validateValue(response.data, schemas.orderListItem, 'data');
    errors.push(...dataErrors);
  }

  if (errors.length > 0) {
    console.group('❌ API Validation Failed: Order Detail Response');
    errors.forEach((error) => console.error(error));
    console.groupEnd();
    return false;
  }

  console.log('✅ API Validation Passed: Order Detail Response');
  return true;
}

/**
 * Generic validator - checks basic response structure
 * @param {Object} response - API response
 * @param {string} endpointName - Endpoint name for logging
 * @returns {boolean} True if valid
 */
export function validateApiResponse(response, endpointName = 'Unknown') {
  if (!VALIDATION_ENABLED) return true;

  const errors = [];

  if (!isObject(response)) {
    console.error(`❌ ${endpointName}: Response is not an object`);
    return false;
  }

  if (!('success' in response)) {
    errors.push('Missing "success" field');
  }

  if (response.success && !('data' in response)) {
    errors.push('Missing "data" field in successful response');
  }

  if (!response.success && !('error' in response)) {
    errors.push('Missing "error" field in failed response');
  }

  if (errors.length > 0) {
    console.group(`❌ API Validation Failed: ${endpointName}`);
    errors.forEach((error) => console.error(error));
    console.groupEnd();
    return false;
  }

  console.log(`✅ API Validation Passed: ${endpointName}`);
  return true;
}

/**
 * Log API call for debugging
 * @param {string} endpoint - API endpoint
 * @param {Object} response - API response
 */
export function logApiCall(endpoint, response) {
  if (!VALIDATION_ENABLED) return;

  console.group(`📡 API Call: ${endpoint}`);
  console.log('Success:', response.success);

  if (response._debug) {
    console.log('Debug Info:', response._debug);
  }

  if (response.pagination) {
    console.log('Pagination:', response.pagination);
  }

  if (response.data) {
    if (Array.isArray(response.data)) {
      console.log(`Data: ${response.data.length} items`);
    } else {
      console.log('Data:', response.data);
    }
  }

  if (response.error) {
    console.error('Error:', response.error);
  }

  console.groupEnd();
}

/**
 * Check for deprecated fields
 * @param {Object} data - Order data
 * @param {string} context - Context for logging
 */
export function checkDeprecatedFields(data, context = 'Data') {
  if (!VALIDATION_ENABLED) return;

  const deprecatedFields = {
    STATUS_ID: 'Use "status" instead',
    ACCOUNT_NUMBER: 'Use "orderNumber" instead',
    DATE_INSERT: 'Use "createdAt" instead',
    RECIPIENT_NAME: 'Use "recipient.name" instead',
    RECIPIENT_PHONE: 'Use "recipient.phone" instead',
  };

  const found = [];
  for (const field in deprecatedFields) {
    if (field in data) {
      found.push(`${field} (${deprecatedFields[field]})`);
    }
  }

  if (found.length > 0) {
    console.group(`⚠️ Deprecated Fields Found: ${context}`);
    found.forEach((msg) => console.warn(msg));
    console.groupEnd();
  }
}

export default {
  validateOrderListResponse,
  validateOrderDetailResponse,
  validateApiResponse,
  logApiCall,
  checkDeprecatedFields,
};
