/**
 * Data formatting utilities
 * Provides functions to format backend data for frontend display
 */

/**
 * Format delivery date for display
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

/**
 * Format order for frontend display
 * @param {Object} order - Backend order object
 * @returns {Object} Formatted order object
 */
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

/**
 * Parse price string from production API ("6 000 ₸" → 6000)
 * @param {string|number} price - Price string or number
 * @returns {number} Price in tenge
 */
const parsePrice = (price) => {
  if (typeof price === 'number') {
    // Local API: price in kopecks
    return Math.floor(price / 100);
  }
  // Production API: string like "6 000 ₸"
  return parseInt(price.replace(/\s+/g, '').replace('₸', '')) || 0;
};

/**
 * Format product for frontend display
 * Supports both local API and production API formats
 * @param {Object} product - Backend product object
 * @returns {Object} Formatted product object
 */
export const formatProductForDisplay = (product) => {
  // Handle both local and production API formats
  const name = product.title || product.name || '';
  const priceInTenge = parsePrice(product.price);
  const discount = parseInt(product.discount) || 0;

  // Calculate original price if there's a discount
  const originalPrice = discount > 0
    ? Math.floor(priceInTenge * 100 / (100 - discount))
    : null;

  // Check if product is new (created within last 7 days)
  // Support both created_at and createdAt
  const createdAt = product.created_at || product.createdAt;
  const isNew = createdAt
    ? (Date.now() - new Date(createdAt).getTime()) < 7 * 24 * 60 * 60 * 1000
    : false;

  // Handle colors - production API returns false or array
  let colors = [];
  if (Array.isArray(product.colors)) {
    colors = product.colors;
  } else if (product.colors && typeof product.colors === 'string') {
    try {
      colors = JSON.parse(product.colors);
    } catch (e) {
      colors = [];
    }
  }

  // Convert backend product format to frontend display format
  return {
    id: product.id,
    name,
    price: priceInTenge,
    originalPrice, // Price before discount (null if no discount)
    discount, // Discount percentage (0-100)
    type: product.type,
    description: product.description || product.composition,
    manufacturingTime: product.manufacturingTime || product.productionTime,
    width: product.width,
    height: product.height,
    catalogWidth: product.catalogWidth || '', // Width for catalog products
    catalogHeight: product.catalogHeight || '', // Height for catalog products
    shelfLife: product.shelfLife,
    enabled: product.enabled !== false, // Production may not have this field
    is_featured: product.is_featured,
    isNew, // Is product created within last 7 days
    colors,
    occasions: product.occasions || [],
    cities: product.cities || [],
    image: product.image,
    images: Array.isArray(product.images) ? product.images : [], // Gallery of all product images
    created_at: createdAt,
    updated_at: product.updated_at
  };
};

/**
 * Format client for frontend display
 * @param {Object} client - Backend client object
 * @returns {Object} Formatted client object
 */
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
