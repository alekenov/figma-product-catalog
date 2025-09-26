// API service for backend communication
const API_BASE_URL = 'http://localhost:8012/api/v1';  // Default port changed to 8012

// Orders API
export const ordersAPI = {
  // Get all orders with optional filtering
  getOrders: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.status) searchParams.append('status', params.status);
    if (params.customer_phone) searchParams.append('customer_phone', params.customer_phone);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/orders/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch orders: ${response.statusText}`);
    }

    return await response.json();
  },

  // Get single order by ID
  getOrder: async (orderId) => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch order: ${response.statusText}`);
    }

    return await response.json();
  },

  // Create new order
  createOrder: async (orderData) => {
    const response = await fetch(`${API_BASE_URL}/orders/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create order: ${response.statusText}`);
    }

    return await response.json();
  },

  // Update order
  updateOrder: async (orderId, orderData) => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      throw new Error(`Failed to update order: ${response.statusText}`);
    }

    return await response.json();
  },

  // Update order status
  updateOrderStatus: async (orderId, status, notes = null) => {
    const params = new URLSearchParams({ status });
    if (notes) params.append('notes', notes);

    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/status?${params.toString()}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to update order status: ${response.statusText}`);
    }

    return await response.json();
  },

  // Add item to order
  addOrderItem: async (orderId, productId, quantity, specialRequests = null) => {
    const params = new URLSearchParams({
      product_id: productId,
      quantity: quantity
    });
    if (specialRequests) params.append('special_requests', specialRequests);

    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/items?${params.toString()}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to add item to order: ${response.statusText}`);
    }

    return await response.json();
  }
};

// Products API
export const productsAPI = {
  // Get all products with optional filtering
  getProducts: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.type) searchParams.append('type', params.type);
    if (params.enabled_only !== undefined) searchParams.append('enabled_only', params.enabled_only);
    if (params.search) searchParams.append('search', params.search);
    if (params.min_price) searchParams.append('min_price', params.min_price);
    if (params.max_price) searchParams.append('max_price', params.max_price);

    const url = `${API_BASE_URL}/products/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.statusText}`);
    }

    return await response.json();
  },

  // Get single product by ID
  getProduct: async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch product: ${response.statusText}`);
    }

    return await response.json();
  },

  // Create new product
  createProduct: async (productData) => {
    const response = await fetch(`${API_BASE_URL}/products/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(productData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create product: ${response.statusText}`);
    }

    return await response.json();
  },

  // Update product
  updateProduct: async (productId, productData) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(productData),
    });

    if (!response.ok) {
      throw new Error(`Failed to update product: ${response.statusText}`);
    }

    return await response.json();
  },

  // Toggle product status
  toggleProductStatus: async (productId, enabled) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}/status?enabled=${enabled}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle product status: ${response.statusText}`);
    }

    return await response.json();
  },

  // Delete product
  deleteProduct: async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete product: ${response.statusText}`);
    }

    return await response.json();
  }
};

// Clients API
export const clientsAPI = {
  // Get all clients with optional filtering
  getClients: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/clients/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch clients: ${response.statusText}`);
    }

    return await response.json();
  },

  // Get single client by phone number
  getClient: async (phone) => {
    const response = await fetch(`${API_BASE_URL}/clients/${encodeURIComponent(phone)}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch client: ${response.statusText}`);
    }

    return await response.json();
  },

  // Get clients dashboard statistics
  getClientStats: async () => {
    const response = await fetch(`${API_BASE_URL}/clients/stats/dashboard`);

    if (!response.ok) {
      throw new Error(`Failed to fetch client stats: ${response.statusText}`);
    }

    return await response.json();
  },

  // Update client notes
  updateClientNotes: async (phone, notes) => {
    const response = await fetch(`${API_BASE_URL}/clients/${encodeURIComponent(phone)}/notes`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ notes }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update client notes: ${response.statusText}`);
    }

    return await response.json();
  }
};

// Helper functions for data transformation
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
    orderNumber: order.orderNumber,
    customerName: order.customerName,
    phone: order.phone,
    status: order.status,
    statusLabel: statusLabels[order.status] || order.status,
    total: `${Math.floor(order.total / 100).toLocaleString()} ₸`,
    date: new Date(order.created_at).toLocaleDateString('ru-RU'),
    time: new Date(order.created_at).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    }),
    delivery_address: order.delivery_address,
    delivery_date: order.delivery_date,
    delivery_notes: order.delivery_notes,
    notes: order.notes,
    items: order.items.map(item => ({
      name: item.product_name,
      quantity: item.quantity,
      price: `${Math.floor(item.product_price / 100).toLocaleString()} ₸`,
      total: `${Math.floor(item.item_total / 100).toLocaleString()} ₸`,
      special_requests: item.special_requests
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