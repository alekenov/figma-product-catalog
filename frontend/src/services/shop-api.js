/**
 * Shop, Profile, and Chats API module  
 * Handles shop settings, user profiles, team management, and chat operations
 */

import { API_BASE_URL, authenticatedFetch, handleApiError, setStoredUser } from './api-client.js';

export const profileAPI = {
  /**
   * Get current user profile
   * @returns {Promise<Object>} User profile data
   */
  getProfile: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/`);

    if (!response.ok) {
      await handleApiError(response);
    }

    const user = await response.json();
    setStoredUser(user);
    return user;
  },

  /**
   * Update user profile
   * @param {Object} profileData Profile update data
   * @returns {Promise<Object>} Updated user profile
   */
  updateProfile: async (profileData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/`, {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const user = await response.json();
    setStoredUser(user);
    return user;
  },

  /**
   * Get team members
   * @param {Object} params Query parameters
   * @returns {Promise<Array>} List of team members
   */
  getTeamMembers: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.role) searchParams.append('role', params.role);
    if (params.active_only !== undefined) searchParams.append('active_only', params.active_only);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/profile/team${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Invite team member
   * @param {Object} invitationData Invitation data (phone, name, role)
   * @returns {Promise<Object>} Invitation details
   */
  inviteTeamMember: async (invitationData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/team/invite`, {
      method: 'POST',
      body: JSON.stringify(invitationData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Remove team member
   * @param {number} userId User ID to remove
   * @returns {Promise<Object>} Success response
   */
  removeTeamMember: async (userId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/team/${userId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Change team member role
   * @param {number} userId User ID
   * @param {string} newRole New role
   * @returns {Promise<Object>} Updated user data
   */
  changeTeamMemberRole: async (userId, newRole) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/team/${userId}/role?new_role=${newRole}`, {
      method: 'PUT',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get team invitations
   * @param {string} status Optional status filter
   * @returns {Promise<Array>} List of invitations
   */
  getTeamInvitations: async (status = null) => {
    const searchParams = new URLSearchParams();
    if (status) searchParams.append('status_filter', status);

    const url = `${API_BASE_URL}/profile/team/invitations${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Cancel team invitation
   * @param {number} invitationId Invitation ID to cancel
   * @returns {Promise<Object>} Success response
   */
  cancelInvitation: async (invitationId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/team/invitations/${invitationId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get team statistics
   * @returns {Promise<Object>} Team stats
   */
  getTeamStats: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/profile/stats`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Shop Settings API
export const shopAPI = {
  /**
   * Get shop settings
   * @returns {Promise<Object>} Shop settings
   */
  getShopSettings: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/shop/settings`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update shop settings
   * @param {Object} settingsData Shop settings data
   * @returns {Promise<Object>} Updated shop settings
   */
  updateShopSettings: async (settingsData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/shop/settings`, {
      method: 'PUT',
      body: JSON.stringify(settingsData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update working hours
   * @param {Object} workingHoursData Working hours data
   * @returns {Promise<Object>} Updated shop settings
   */
  updateWorkingHours: async (workingHoursData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/shop/working-hours`, {
      method: 'PUT',
      body: JSON.stringify(workingHoursData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update delivery settings
   * @param {Object} deliveryData Delivery settings data
   * @returns {Promise<Object>} Updated shop settings
   */
  updateDeliverySettings: async (deliveryData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/shop/delivery`, {
      method: 'PUT',
      body: JSON.stringify(deliveryData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Orders API
export const chatsAPI = {
  /**
   * Get all chat sessions with optional filtering
   * @param {Object} params Query parameters
   * @returns {Promise<Array>} Chat sessions data
   */
  getChats: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.channel) searchParams.append('channel', params.channel);
    if (params.date_from) searchParams.append('date_from', params.date_from);
    if (params.date_to) searchParams.append('date_to', params.date_to);
    if (params.has_order !== undefined) searchParams.append('has_order', params.has_order);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/chats/admin${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get single chat session with messages
   * @param {string|number} sessionId Session ID
   * @returns {Promise<Object>} Chat session with messages
   */
  getChatDetail: async (sessionId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/chats/admin/${sessionId}`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get chat statistics
   * @returns {Promise<Object>} Chat statistics
   */
  getStats: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/chats/stats`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Helper functions for data transformation

/**
 * Format delivery date with "Today/Tomorrow" support
 * @param {string} isoDateString - ISO date string (e.g., "2025-10-08T14:00:00")
 * @returns {string} Formatted date (e.g., "Сегодня, 14:00" or "8 октября, 14:00")
 */
