// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV
    ? 'http://localhost:8014/api/v1'  // Local development
    : 'https://figma-catalog-api.onrender.com/api/v1'  // Production
  );

export const API_ENDPOINTS = {
  // Products
  products: `${API_BASE_URL}/products`,
  productById: (id) => `${API_BASE_URL}/products/${id}`,

  // Orders
  orders: `${API_BASE_URL}/orders`,
  orderById: (id) => `${API_BASE_URL}/orders/${id}`,

  // Clients
  clients: `${API_BASE_URL}/clients`,
  clientById: (id) => `${API_BASE_URL}/clients/${id}`,

  // Warehouse
  warehouse: `${API_BASE_URL}/warehouse`,
  warehouseItem: (id) => `${API_BASE_URL}/warehouse/${id}`,

  // Recipes
  recipes: `${API_BASE_URL}/recipes`,
  recipeById: (id) => `${API_BASE_URL}/recipes/${id}`,

  // Inventory
  inventory: `${API_BASE_URL}/inventory`,
  inventoryItem: (id) => `${API_BASE_URL}/inventory/${id}`,

  // Auth
  login: `${API_BASE_URL}/auth/login`,
  register: `${API_BASE_URL}/auth/register`,
  profile: `${API_BASE_URL}/profile/me`,

  // Shop
  shop: `${API_BASE_URL}/shop`,
  shopItem: (id) => `${API_BASE_URL}/shop/${id}`,
};

// API helper functions
export const apiRequest = async (url, options = {}) => {
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // Add auth token if exists
  const token = localStorage.getItem('authToken');
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export default API_BASE_URL;