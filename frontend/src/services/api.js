// API service for backend communication
const DEFAULT_API_BASE_URL = 'http://localhost:8014/api/v1'; // Local development backend
const sanitizeBaseUrl = (value) => {
  if (!value) return null;
  return value.endsWith('/') ? value.slice(0, -1) : value;
};

export const API_BASE_URL = sanitizeBaseUrl(import.meta.env?.VITE_API_BASE_URL) || DEFAULT_API_BASE_URL;

// Token management
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

/**
 * Get stored authentication token
 * @returns {string|null} JWT token or null
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Store authentication token
 * @param {string} token JWT token
 */
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Remove authentication token
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

/**
 * Get stored user data
 * @returns {Object|null} User data or null
 */
export const getStoredUser = () => {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
};

/**
 * Store user data
 * @param {Object} user User data
 */
export const setStoredUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

/**
 * Create authenticated fetch request with automatic token inclusion
 * @param {string} url Request URL
 * @param {Object} options Fetch options
 * @returns {Promise<Response>} Fetch response
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = getToken();

  const isFormData =
    typeof FormData !== 'undefined' && options.body instanceof FormData;

  const headers = {
    ...(options.headers || {}),
  };

  const hasContentTypeHeader = Object.keys(headers).some(
    (key) => key.toLowerCase() === 'content-type'
  );

  if (isFormData) {
    // Let the browser set the proper multipart boundary
    for (const key of Object.keys(headers)) {
      if (key.toLowerCase() === 'content-type') {
        delete headers[key];
      }
    }
  } else if (!hasContentTypeHeader) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  let response = await fetch(url, config);

  // Handle token expiration - try to refresh token
  if (response.status === 401 && token) {
    try {
      const refreshResponse = await authAPI.refresh();
      if (refreshResponse.access_token) {
        setToken(refreshResponse.access_token);
        setStoredUser(refreshResponse.user);

        // Retry original request with new token
        config.headers['Authorization'] = `Bearer ${refreshResponse.access_token}`;
        response = await fetch(url, config);
      }
    } catch (refreshError) {
      // Refresh failed, redirect to login
      removeToken();
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      throw new Error('Сессия истекла. Пожалуйста, войдите в систему снова.');
    }
  }

  return response;
};

/**
 * Handle API errors with Russian messages
 * @param {Response} response Fetch response
 * @returns {Promise<never>} Throws formatted error
 */
const handleApiError = async (response) => {
  let errorMessage = 'Произошла ошибка при обращении к серверу';

  try {
    const errorData = await response.json();
    if (errorData.detail) {
      // Handle Pydantic validation errors (array of error objects)
      if (Array.isArray(errorData.detail)) {
        const errors = errorData.detail.map(err => {
          // Handle different error formats
          if (err.msg) {
            // Translate common validation messages
            const validationMappings = {
              'Field required': 'Обязательное поле',
              'Input should be': 'Неверное значение',
              'Phone number already in use': 'Этот номер телефона уже используется',
              'ensure this value has at least': 'Минимальная длина',
              'value is not a valid': 'Недопустимое значение'
            };

            // Check if message starts with any known pattern
            for (const [eng, rus] of Object.entries(validationMappings)) {
              if (err.msg.includes(eng)) {
                return rus;
              }
            }

            // Special handling for enum errors
            if (err.msg.includes("Input should be 'director', 'manager', 'florist' or 'courier'")) {
              return 'Роль должна быть: директор, менеджер, флорист или курьер';
            }

            return err.msg;
          }
          return 'Ошибка валидации';
        });
        errorMessage = errors.join(', ');
      } else if (typeof errorData.detail === 'string') {
        // Map common English errors to Russian
        const errorMappings = {
          'Incorrect phone number or password': 'Неверный номер телефона или пароль',
          'Phone number already registered': 'Этот номер телефона уже зарегистрирован',
          'Current password is incorrect': 'Текущий пароль неверен',
          'New password must be at least 6 characters long': 'Новый пароль должен содержать не менее 6 символов',
          'Only managers and directors can change user roles': 'Только менеджеры и директора могут изменять роли пользователей',
          'Phone number already in use': 'Этот номер телефона уже используется',
          'User with this phone number already exists': 'Пользователь с таким номером телефона уже существует',
          'Token is invalid or expired': 'Токен недействителен или истек',
          'User not found': 'Пользователь не найден',
          'Cannot remove yourself from the team': 'Нельзя удалить себя из команды',
          'Only directors can remove other directors': 'Только директора могут удалять других директоров',
          'Only directors can manage director roles': 'Только директора могут управлять ролями директоров',
          'Cannot demote yourself from director role': 'Нельзя понизить себя с должности директора',
          'Cannot demote the last director. At least one director must remain': 'Нельзя понизить последнего директора. Должен остаться хотя бы один директор'
        };

        errorMessage = errorMappings[errorData.detail] || errorData.detail;
      } else {
        // detail is an object or other type
        errorMessage = JSON.stringify(errorData.detail);
      }
    }
  } catch (parseError) {
    // If can't parse JSON, use status-based message
    switch (response.status) {
      case 400:
        errorMessage = 'Неверные данные запроса';
        break;
      case 401:
        errorMessage = 'Необходима авторизация';
        break;
      case 403:
        errorMessage = 'Недостаточно прав доступа';
        break;
      case 404:
        errorMessage = 'Ресурс не найден';
        break;
      case 422:
        errorMessage = 'Ошибка валидации данных';
        break;
      case 500:
        errorMessage = 'Внутренняя ошибка сервера';
        break;
    }
  }

  throw new Error(errorMessage);
};

// Authentication API
export const authAPI = {
  /**
   * Login user with phone and password
   * @param {string} phone Phone number in Kazakhstan format
   * @param {string} password User password
   * @returns {Promise<Object>} Login response with token and user data
   */
  login: async (phone, password) => {
    console.log('🌐 [API] Login request starting...');
    console.log('   URL:', `${API_BASE_URL}/auth/login`);
    console.log('   Phone:', phone);
    console.log('   Password length:', password.length);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
    });

    console.log('📡 [API] Response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });

    if (!response.ok) {
      console.error('❌ [API] Login failed with status:', response.status);
      await handleApiError(response);
    }

    const data = await response.json();
    console.log('✅ [API] Login successful, user:', data.user?.name);

    // Store token and user data
    setToken(data.access_token);
    setStoredUser(data.user);
    console.log('💾 [API] Token and user stored in localStorage');

    return data;
  },

  /**
   * Refresh JWT token for current user
   * @returns {Promise<Object>} New token and user data
   */
  refresh: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const data = await response.json();

    // Update stored token and user data
    setToken(data.access_token);
    setStoredUser(data.user);

    return data;
  },

  /**
   * Logout current user
   * @returns {Promise<Object>} Logout response
   */
  logout: async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
      });

      const data = response.ok ? await response.json() : null;
      return data;
    } finally {
      // Always clear local storage regardless of API response
      removeToken();
    }
  },

  /**
   * Get current user information
   * @returns {Promise<Object>} Current user data
   */
  me: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/me`);

    if (!response.ok) {
      await handleApiError(response);
    }

    const user = await response.json();
    setStoredUser(user);
    return user;
  },

  /**
   * Register new user
   * @param {Object} userData User registration data
   * @returns {Promise<Object>} Created user data
   */
  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Change user password
   * @param {string} currentPassword Current password
   * @param {string} newPassword New password
   * @returns {Promise<Object>} Success response
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/change-password`, {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Verify if current token is valid
   * @returns {Promise<Object>} Token verification result
   */
  verifyToken: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/verify-token`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} True if user has valid token
   */
  isAuthenticated: () => {
    const token = getToken();
    const user = getStoredUser();
    return !!(token && user);
  }
};

// Profile and Team Management API
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
export const ordersAPI = {
  /**
   * Get all orders with optional filtering
   * @param {Object} params Query parameters
   * @returns {Promise<Object>} Orders data with pagination
   */
  getOrders: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.status) searchParams.append('status', params.status);
    if (params.customer_phone) searchParams.append('customer_phone', params.customer_phone);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/orders/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get single order by ID
   * @param {string|number} orderId Order ID
   * @returns {Promise<Object>} Order data
   */
  getOrder: async (orderId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create new order
   * @param {Object} orderData Order data
   * @returns {Promise<Object>} Created order
   */
  createOrder: async (orderData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/`, {
      method: 'POST',
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create new order with items
   * @param {Object} orderData Order data with items
   * @returns {Promise<Object>} Created order
   */
  createOrderWithItems: async (orderData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/with-items`, {
      method: 'POST',
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update order
   * @param {string|number} orderId Order ID
   * @param {Object} orderData Order data
   * @returns {Promise<Object>} Updated order
   */
  updateOrder: async (orderId, orderData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}`, {
      method: 'PUT',
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update order status
   * @param {string|number} orderId Order ID
   * @param {string} status New order status
   * @param {string|null} notes Optional notes
   * @returns {Promise<Object>} Updated order
   */
  updateOrderStatus: async (orderId, status, notes = null) => {
    const params = new URLSearchParams({ status });
    if (notes) params.append('notes', notes);

    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}/status?${params.toString()}`, {
      method: 'PATCH',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Add item to order
   * @param {string|number} orderId Order ID
   * @param {string|number} productId Product ID
   * @param {number} quantity Item quantity
   * @param {string|null} specialRequests Optional special requests
   * @returns {Promise<Object>} Updated order
   */
  addOrderItem: async (orderId, productId, quantity, specialRequests = null) => {
    const params = new URLSearchParams({
      product_id: productId,
      quantity: quantity
    });
    if (specialRequests) params.append('special_requests', specialRequests);

    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}/items?${params.toString()}`, {
      method: 'POST',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Upload photo for order (before delivery)
   * @param {string|number} orderId Order ID
   * @param {File} file Image file
   * @returns {Promise<Object>} Upload result with photo URL
   */
  uploadOrderPhoto: async (orderId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    // For FormData, we need to let the browser set Content-Type with boundary
    // So we use fetch directly instead of authenticatedFetch
    const token = getToken();
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/photo`, {
      method: 'POST',
      body: formData,
      headers: headers
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Delete photo from order
   * @param {string|number} orderId Order ID
   * @returns {Promise<Object>} Delete result
   */
  deleteOrderPhoto: async (orderId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}/photo`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Products API
export const productsAPI = {
  /**
   * Get all products with optional filtering
   * @param {Object} params Query parameters
   * @returns {Promise<Object>} Products data with pagination
   */
  getProducts: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.type) searchParams.append('type', params.type);
    if (params.enabled_only !== undefined) searchParams.append('enabled_only', params.enabled_only);
    if (params.search) searchParams.append('search', params.search);
    if (params.min_price) searchParams.append('min_price', params.min_price);
    if (params.max_price) searchParams.append('max_price', params.max_price);

    const url = `${API_BASE_URL}/products/admin${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get single product by ID
   * @param {string|number} productId Product ID
   * @returns {Promise<Object>} Product data
   */
  getProduct: async (productId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create new product
   * @param {Object} productData Product data
   * @returns {Promise<Object>} Created product
   */
  createProduct: async (productData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/`, {
      method: 'POST',
      body: JSON.stringify(productData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update product
   * @param {string|number} productId Product ID
   * @param {Object} productData Product data
   * @returns {Promise<Object>} Updated product
   */
  updateProduct: async (productId, productData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Toggle product status
   * @param {string|number} productId Product ID
   * @param {boolean} enabled Enable/disable status
   * @returns {Promise<Object>} Updated product
   */
  toggleProductStatus: async (productId, enabled) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}/status?enabled=${enabled}`, {
      method: 'PATCH',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Delete product
   * @param {string|number} productId Product ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  deleteProduct: async (productId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Clients API
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
export const formatDeliveryDate = (isoDateString) => {
  if (!isoDateString) return '';

  // Ensure UTC timezone if missing (backend returns naive datetime)
  let dateStr = isoDateString;
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
    dateStr += 'Z';
  }

  const date = new Date(dateStr);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  // Extract time
  const timeStr = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

  // Check if today
  if (date.toDateString() === today.toDateString()) {
    return `Сегодня, ${timeStr}`;
  }

  // Check if tomorrow
  if (date.toDateString() === tomorrow.toDateString()) {
    return `Завтра, ${timeStr}`;
  }

  // Other dates - show day and month
  const day = date.getDate();
  const month = date.toLocaleDateString('ru-RU', { month: 'long' });

  return `${day} ${month}, ${timeStr}`;
};

export const formatOrderForDisplay = (order) => {
  // Convert backend order format to frontend display format
  const statusLabels = {
    'new': 'Новый',
    'paid': 'Оплачен',
    'accepted': 'Принят',
    'assembled': 'Собран',
    'in_delivery': 'В пути',
    'delivered': 'Доставлен',
    'cancelled': 'Отменён'
  };

  return {
    id: order.id,
    tracking_id: order.tracking_id,
    orderNumber: order.orderNumber,
    customerName: order.customerName,
    phone: order.phone,
    customer_email: order.customer_email,
    status: order.status,
    statusLabel: statusLabels[order.status] || order.status,
    total: `${Math.floor(order.total / 100).toLocaleString()} ₸`,
    totalRaw: order.total, // Keep raw value in kopecks for calculations
    date: new Date(order.created_at).toLocaleDateString('ru-RU'),
    time: new Date(order.created_at).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    }),
    delivery_address: order.delivery_address,
    delivery_date: formatDeliveryDate(order.delivery_date),
    delivery_date_raw: order.delivery_date, // Keep original for editing
    delivery_notes: order.delivery_notes,
    notes: order.notes,
    // Kaspi Pay fields
    payment_method: order.payment_method,
    kaspi_payment_id: order.kaspi_payment_id,
    kaspi_payment_status: order.kaspi_payment_status,
    kaspi_payment_created_at: order.kaspi_payment_created_at,
    kaspi_payment_completed_at: order.kaspi_payment_completed_at,
    // Team assignment fields
    assigned_to: order.assigned_to,
    assigned_to_name: order.assigned_to_name,
    courier: order.courier,
    courier_name: order.courier_name,
    items: (order.items || []).map(item => ({
      name: item.product_name,
      description: item.product_description,
      quantity: item.quantity,
      price: `${Math.floor(item.product_price / 100).toLocaleString()} ₸`,
      total: `${Math.floor(item.item_total / 100).toLocaleString()} ₸`,
      special_requests: item.special_requests
    })),
    photos: (order.photos || []).map(photo => ({
      url: photo.photo_url,
      label: photo.label,
      type: photo.photo_type,
      feedback: photo.client_feedback,
      comment: photo.client_comment
    }))
  };
};

export const formatProductForDisplay = (product) => {
  // Convert backend product format to frontend display format
  return {
    id: product.id,
    name: product.name,
    price: Math.floor(product.price / 100), // Convert from kopecks to tenge
    type: product.type,
    description: product.description,
    manufacturingTime: product.manufacturingTime,
    width: product.width,
    height: product.height,
    shelfLife: product.shelfLife,
    enabled: product.enabled,
    is_featured: product.is_featured,
    colors: product.colors || [],
    occasions: product.occasions || [],
    cities: product.cities || [],
    image: product.image,
    created_at: product.created_at,
    updated_at: product.updated_at
  };
};

export const formatClientForDisplay = (client) => {
  // Convert backend client format to frontend display format
  return {
    id: client.id,
    phone: client.phone,
    customerName: client.customerName || "Клиент без имени",
    customer_since: client.customer_since,
    total_orders: client.total_orders,
    total_spent: `${Math.floor(client.total_spent / 100).toLocaleString()} ₸`,
    total_spent_raw: client.total_spent,
    average_order: `${Math.floor(client.average_order / 100).toLocaleString()} ₸`,
    average_order_raw: client.average_order,
    last_order_number: client.last_order_number,
    last_order_status: client.last_order_status,
    first_order_date: client.first_order_date,
    last_order_date: client.last_order_date
  };
};
