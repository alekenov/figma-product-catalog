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
 * Format product for frontend display
 * @param {Object} product - Backend product object
 * @returns {Object} Formatted product object
 */
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
