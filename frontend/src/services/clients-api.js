/**
 * Clients API module
 * Handles client/customer management operations
 */

import { API_BASE_URL, authenticatedFetch, handleApiError } from './api-client.js';

export const clientsAPI = {
  /**
   * Get all clients with optional filtering
   * @param {Object} params Query parameters
   * @returns {Promise<Object>} Clients data with pagination
   */
  getClients: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/clients/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create a new client
   * @param {Object} clientData Client data
   * @returns {Promise<Object>} Created client data
   */
  createClient: async (clientData) => {
    const response = await fetch(`${API_BASE_URL}/clients/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(clientData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create client');
    }
    return await response.json();
  },
  /**
   * Get single client by ID
   * @param {string|number} clientId Client ID
   * @returns {Promise<Object>} Client data
   */
  getClient: async (clientId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/clients/${clientId}`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get clients dashboard statistics
   * @returns {Promise<Object>} Client statistics
   */
  getClientStats: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/clients/stats/dashboard`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update client notes
   * @param {string|number} clientId Client ID
   * @param {string} notes Client notes
   * @returns {Promise<Object>} Updated client data
   */
  updateClientNotes: async (clientId, notes) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/clients/${clientId}/notes`, {
      method: 'PUT',
      body: JSON.stringify({ notes }),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update client information (name, phone, notes)
   * @param {string|number} clientId Client ID
   * @param {Object} clientData Client data to update
   * @param {string} clientData.customerName Client name (optional)
   * @param {string} clientData.phone Client phone (optional)
   * @param {string} clientData.notes Client notes (optional)
   * @returns {Promise<Object>} Updated client data
   */
  updateClient: async (clientId, clientData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/clients/${clientId}`, {
      method: 'PUT',
      body: JSON.stringify(clientData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Chats API
