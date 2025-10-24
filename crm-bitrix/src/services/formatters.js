/**
 * Data formatting utilities
 * Provides functions to format backend data for frontend display
 * Updated: 2025-10-24 - Fixed empty string handling
 */

/**
 * Format delivery date for display with smart relative times
 * @param {string} isoDateString - ISO date string (e.g., "2025-10-08T14:00:00")
 * @returns {string} Formatted date (e.g., "через 2 часа", "сегодня в 14:00", "26 октября")
 */
export const formatDeliveryDate = (isoDateString) => {
  if (!isoDateString) return '';

  // Ensure UTC timezone if missing (backend returns naive datetime)
  let dateStr = isoDateString;
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
    dateStr += 'Z';
  }

  const date = new Date(dateStr);
  const now = new Date();

  // Calculate difference in milliseconds
  const diffMs = date.getTime() - now.getTime();
  const diffMinutes = Math.round(diffMs / (1000 * 60));
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));

  // If delivery is in the future and within 24 hours
  if (diffMs > 0 && diffHours < 24) {
    if (diffMinutes < 60) {
      return `через ${diffMinutes} мин`;
    } else if (diffHours < 24) {
      const hours = Math.floor(diffMs / (1000 * 60 * 60));
      return `через ${hours} ${hours === 1 ? 'час' : hours < 5 ? 'часа' : 'часов'}`;
    }
  }

  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  // Extract time
  const timeStr = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

  // Check if today
  if (date.toDateString() === today.toDateString()) {
    return `сегодня в ${timeStr}`;
  }

  // Check if tomorrow
  if (date.toDateString() === tomorrow.toDateString()) {
    return `завтра в ${timeStr}`;
  }

  // Other dates - show day and month WITHOUT year
  const day = date.getDate();
  const month = date.toLocaleDateString('ru-RU', { month: 'long' });

  return `${day} ${month}`;
};

/**
 * Format relative time (e.g., "2 часа назад", "5 минут назад")
 * @param {string} isoDateString - ISO date string
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (isoDateString) => {
  if (!isoDateString) return '';

  // Ensure UTC timezone if missing
  let dateStr = isoDateString;
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
    dateStr += 'Z';
  }

  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.round(diffMs / (1000 * 60));
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (diffMinutes < 1) {
    return 'только что';
  } else if (diffMinutes < 60) {
    return `${diffMinutes} ${diffMinutes === 1 ? 'минуту' : diffMinutes < 5 ? 'минуты' : 'минут'} назад`;
  } else if (diffHours < 24) {
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    return `${hours} ${hours === 1 ? 'час' : hours < 5 ? 'часа' : 'часов'} назад`;
  } else if (diffDays === 1) {
    return 'вчера';
  } else if (diffDays < 7) {
    return `${diffDays} ${diffDays < 5 ? 'дня' : 'дней'} назад`;
  } else {
    // For older dates, show actual date without year
    const day = date.getDate();
    const month = date.toLocaleDateString('ru-RU', { month: 'long' });
    return `${day} ${month}`;
  }
};

/**
 * Format date without year (e.g., "24 октября в 15:46")
 * @param {string} isoDateString - ISO date string
 * @returns {string} Formatted date without year
 */
export const formatDateWithoutYear = (isoDateString) => {
  if (!isoDateString) return '';

  const date = new Date(isoDateString);
  const day = date.getDate();
  const month = date.toLocaleDateString('ru-RU', { month: 'long' });
  const timeStr = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

  return `${day} ${month} в ${timeStr}`;
};

/**
 * Format date only without time (e.g., "сегодня", "завтра", "24 октября")
 * @param {string} dateString - Date string (ISO or simple date)
 * @returns {string} Formatted date without time
 */
export const formatDateOnly = (dateString) => {
  if (!dateString) return '';

  const date = new Date(dateString);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  // Check if today
  if (date.toDateString() === today.toDateString()) {
    return 'сегодня';
  }

  // Check if tomorrow
  if (date.toDateString() === tomorrow.toDateString()) {
    return 'завтра';
  }

  // Other dates - show day and month WITHOUT year
  const day = date.getDate();
  const month = date.toLocaleDateString('ru-RU', { month: 'long' });

  return `${day} ${month}`;
};

/**
 * Convert relative image path to full URL
 * @param {string} imagePath - Image path (relative or absolute)
 * @returns {string} Full URL
 */
const formatImageUrl = (imagePath) => {
  if (!imagePath) return '';
  if (imagePath.startsWith('http')) return imagePath;
  return `https://cvety.kz${imagePath}`;
};

/**
 * Format order for frontend display
 * @param {Object} order - Backend order object (from adaptOrder)
 * @returns {Object} Formatted order object
 */
export const formatOrderForDisplay = (order) => {
  // Convert backend order format to frontend display format
  // Status labels for both uppercase (NEW, ACCEPTED) and lowercase (new, accepted)
  const statusLabels = {
    'NEW': 'Новый',
    'PAID': 'Оплачен',
    'ACCEPTED': 'Принят',
    'IN_PRODUCTION': 'Собран',
    'IN_DELIVERY': 'В пути',
    'DELIVERED': 'Доставлен',
    'CANCELLED': 'Отменён',
    // Lowercase variants for backward compatibility
    'new': 'Новый',
    'paid': 'Оплачен',
    'accepted': 'Принят',
    'assembled': 'Собран',
    'in_delivery': 'В пути',
    'delivered': 'Доставлен',
    'cancelled': 'Отменён'
  };

  // Format price with currency support
  const formatPrice = (price, currency = 'KZT') => {
    if (currency === 'USD') {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
    } else if (currency === 'EUR') {
      return `€${price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
    } else {
      // KZT - Bitrix returns whole tenge, not kopecks
      return `${Math.floor(price).toLocaleString()} ₸`;
    }
  };

  // Helper to check if string has content
  const hasContent = (str) => str && str.trim().length > 0;

  const result = {
    id: order.id,
    tracking_id: order.tracking_id,
    orderNumber: order.order_number,
    customerName: order.is_pickup
      ? (hasContent(order.sender_name) ? order.sender_name.trim() : 'Заказчик не указан')
      : (hasContent(order.recipient_name)
          ? order.recipient_name.trim()
          : (hasContent(order.sender_name)
              ? order.sender_name.trim()
              : 'Получатель не указан')),
    phone: order.customer_phone || order.sender_phone || '',
    customer_email: order.customer_email || order.sender_email || '',
    status: order.status?.toLowerCase() || 'new', // Convert to lowercase for UI filters
    statusLabel: statusLabels[order.status] || order.status,
    total: formatPrice(order.total_price, order.currency),
    totalRaw: order.total_price, // Keep raw value for calculations
    createdAt: formatRelativeTime(order.created_at), // "2 часа назад"
    createdAtDetailed: formatDateWithoutYear(order.created_at), // "24 октября в 15:46"
    delivery_address: order.is_pickup
      ? (hasContent(order.delivery_address) ? `Самовывоз: ${order.delivery_address}` : 'Самовывоз')
      : (order.ask_address
        ? 'Уточнить у получателя'
        : (hasContent(order.delivery_address) ? order.delivery_address.trim() : 'Адрес не указан')),
    delivery_date: order.delivery_time
      ? `${formatDateOnly(order.delivery_date)} ${order.delivery_time}`
      : formatDeliveryDate(order.delivery_date),
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
    // Image (from list endpoint - mainImage, or detail endpoint)
    main_image: formatImageUrl(order.main_image),

    // Sender and recipient info
    sender_name: order.sender_name || '',
    sender_phone: order.sender_phone || '',
    sender_email: order.sender_email || '',
    recipient_name: order.recipient_name || '',
    recipient_phone: order.recipient_phone || '',

    // Order details
    postcard_text: order.postcard_text || '',
    comment: order.comment || '',

    // Delivery (use RAW deliveryPrice, not formatted)
    delivery_time: order.delivery_time || '',
    delivery_price: order.delivery_price || 0,
    currency: order.currency || 'KZT',

    // Payment
    is_paid: order.is_paid || false,

    // Executors and history
    executors: order.executors || [],
    history: order.history || [],

    // Photos
    assembled_photo: formatImageUrl(order.assembled_photo),
    recipient_photo: formatImageUrl(order.recipient_photo),

    items: (order.items || []).map(item => ({
      id: item.id,
      name: item.name || item.product_name,
      description: item.description || item.product_description,
      quantity: item.quantity,
      price: formatPrice(item.price, item.currency),
      priceRaw: item.price,
      total: item.price * item.quantity,
      currency: item.currency || 'KZT',
      image: formatImageUrl(item.image || item.image_big),
      special_requests: item.special_requests
    })),
    photos: (order.photos || []).map(photo => ({
      url: formatImageUrl(photo.photo_url),
      label: photo.label,
      type: photo.photo_type,
      feedback: photo.client_feedback,
      comment: photo.client_comment
    }))
  };

  // Debug: log formatted result
  console.log('🔧 formatOrderForDisplay returning for order:', result?.id, 'executors:', result?.executors?.length || 0);

  return result;
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
