/**
 * Base API client for backend communication
 * Provides core functionality for HTTP requests, token management, and error handling
 */

const DEFAULT_API_BASE_URL = 'http://localhost:8014/api/v1'; // Local development backend

const sanitizeBaseUrl = (value) => {
  if (!value) return null;
  return value.endsWith('/') ? value.slice(0, -1) : value;
};

export const API_BASE_URL = sanitizeBaseUrl(import.meta.env?.VITE_API_BASE_URL) || DEFAULT_API_BASE_URL;

// Token management keys
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
      // Import auth API to avoid circular dependency
      // This will be resolved when auth-api.js is created
      const { authAPI } = await import('./auth-api.js');
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
export const handleApiError = async (response) => {
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
