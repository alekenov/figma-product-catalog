/**
 * Payment Service API Client
 *
 * Communicates with payment-service microservice for:
 * - Payment configuration management (БИН routing)
 * - Payment audit logs
 * - Test payment creation
 */

// Payment service URL (different from main backend)
const DEFAULT_PAYMENT_SERVICE_URL = 'https://payment-service-production-a685.up.railway.app';
const sanitizeBaseUrl = (value) => {
  if (!value) return null;
  return value.endsWith('/') ? value.slice(0, -1) : value;
};

export const PAYMENT_SERVICE_URL = sanitizeBaseUrl(import.meta.env?.VITE_PAYMENT_SERVICE_URL) || DEFAULT_PAYMENT_SERVICE_URL;

/**
 * Handle API errors
 * @param {Response} response Fetch response
 * @throws {Error} Formatted error message
 */
const handleApiError = async (response) => {
  let errorMessage = `HTTP ${response.status}`;

  try {
    const errorData = await response.json();
    errorMessage = errorData.detail || errorData.message || errorMessage;
  } catch {
    // If response is not JSON, use status text
    errorMessage = response.statusText || errorMessage;
  }

  throw new Error(errorMessage);
};

/**
 * Payment API methods
 */
export const paymentAPI = {
  /**
   * Get all payment configurations
   * @returns {Promise<Array>} Payment configurations
   */
  getConfigs: async () => {
    const response = await fetch(`${PAYMENT_SERVICE_URL}/admin/configs`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create new payment configuration
   * @param {Object} config Configuration data
   * @param {number} config.shop_id Shop ID
   * @param {string} config.organization_bin 12-digit БИН
   * @param {boolean} config.is_active Active status
   * @param {string} config.provider Provider name (e.g., "kaspi")
   * @param {string} [config.description] Optional description
   * @returns {Promise<Object>} Created configuration
   */
  createConfig: async (config) => {
    const response = await fetch(`${PAYMENT_SERVICE_URL}/admin/configs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update payment configuration
   * @param {number} shop_id Shop ID (primary key for updates)
   * @param {Object} updates Fields to update
   * @returns {Promise<Object>} Updated configuration
   */
  updateConfig: async (shop_id, updates) => {
    const response = await fetch(`${PAYMENT_SERVICE_URL}/admin/configs/${shop_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Delete payment configuration
   * @param {number} id Configuration ID
   * @returns {Promise<void>}
   */
  deleteConfig: async (id) => {
    const response = await fetch(`${PAYMENT_SERVICE_URL}/admin/configs/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }
  },

  /**
   * Get payment audit logs
   * @param {Object} params Query parameters
   * @param {number} [params.shop_id] Filter by shop ID
   * @param {string} [params.operation_type] Filter by operation (create/status/refund)
   * @param {number} [params.limit=50] Number of logs to return
   * @param {number} [params.skip=0] Number of logs to skip
   * @returns {Promise<Array>} Payment logs
   */
  getLogs: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.shop_id) searchParams.append('shop_id', params.shop_id);
    if (params.operation_type) searchParams.append('operation_type', params.operation_type);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.skip) searchParams.append('skip', params.skip);

    const url = `${PAYMENT_SERVICE_URL}/admin/logs${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create test payment
   * @param {Object} payment Payment data
   * @param {number} payment.shop_id Shop ID
   * @param {string} payment.phone Customer phone
   * @param {number} payment.amount Amount in tenge
   * @param {string} payment.message Payment description
   * @returns {Promise<Object>} Payment creation response
   */
  createTestPayment: async (payment) => {
    const response = await fetch(`${PAYMENT_SERVICE_URL}/payments/kaspi/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payment),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Check payment status
   * @param {string} externalId Payment external ID
   * @returns {Promise<Object>} Payment status
   */
  checkPaymentStatus: async (externalId) => {
    const response = await fetch(
      `${PAYMENT_SERVICE_URL}/payments/kaspi/status/${externalId}`
    );

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },
};

/**
 * Format payment config for display
 * @param {Object} config Raw configuration from API
 * @returns {Object} Formatted configuration
 */
export const formatPaymentConfigForDisplay = (config) => {
  return {
    ...config,
    createdAt: new Date(config.created_at).toLocaleString('ru-RU'),
    updatedAt: new Date(config.updated_at).toLocaleString('ru-RU'),
    statusText: config.is_active ? 'Активен' : 'Неактивен',
    statusColor: config.is_active ? 'text-green-600' : 'text-gray-400',
  };
};

/**
 * Format payment log for display
 * @param {Object} log Raw log from API
 * @returns {Object} Formatted log
 */
export const formatPaymentLogForDisplay = (log) => {
  return {
    ...log,
    timestamp: new Date(log.timestamp).toLocaleString('ru-RU'),
    amountTenge: log.amount ? `${Math.floor(log.amount / 100)} ₸` : '-',
    operationText: {
      create: 'Создание',
      status: 'Проверка статуса',
      refund: 'Возврат',
    }[log.operation_type] || log.operation_type,
    statusColor: {
      success: 'text-green-600',
      failed: 'text-red-600',
      pending: 'text-yellow-600',
    }[log.status] || 'text-gray-600',
  };
};
