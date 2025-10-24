/**
 * Data adapters to convert Bitrix API v2 format to internal format (v1 compatible)
 * Handles type conversions, field mappings, and data transformations
 */

/**
 * Parse price string from Bitrix format to kopecks
 * Example: "4 950 ₸" → 495000 (kopecks)
 * @param {string} priceStr - Price string with currency symbol
 * @returns {number} - Price in kopecks
 */
function parsePrice(priceStr) {
  if (!priceStr) return 0;

  // Remove all non-numeric characters except digits
  const cleaned = priceStr.toString().replace(/[^0-9]/g, '');
  const tenge = parseInt(cleaned, 10);

  // Convert tenge to kopecks
  return tenge * 100;
}

/**
 * Format price from kopecks to display format
 * Example: 495000 (kopecks) → "4 950 ₸"
 * @param {number} kopecks - Price in kopecks
 * @returns {string} - Formatted price string
 */
function formatPrice(kopecks) {
  if (!kopecks) return '0 ₸';

  const tenge = kopecks / 100;
  const formatted = tenge.toLocaleString('ru-KZ');

  return `${formatted} ₸`;
}

/**
 * Map Bitrix order status codes to internal format
 * @param {string} statusKey - Bitrix status key
 * @returns {string} - Internal status code
 */
function adaptOrderStatus(statusKey) {
  const statusMap = {
    // Modern API status keys (lowercase)
    'new': 'NEW',
    'accepted': 'ACCEPTED',
    'assembled': 'IN_PRODUCTION',
    'in_delivery': 'IN_DELIVERY',
    'delivered': 'DELIVERED',
    'cancelled': 'CANCELLED',
    // Legacy Bitrix status codes (uppercase)
    'N': 'NEW',
    'AP': 'ACCEPTED',
    'AS': 'IN_PRODUCTION',  // Assembled
    'CO': 'IN_PRODUCTION',  // Completed/Собран
    'ID': 'IN_DELIVERY',
    'D': 'DELIVERED',
    'C': 'CANCELLED'
  };

  return statusMap[statusKey] || statusMap[statusKey?.toLowerCase()] || statusKey?.toUpperCase() || 'NEW';
}

const toTenge = (value) => {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return 0;
  }
  return Math.round(Number(value) / 100);
};

const toKopecks = (value) => {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return 0;
  }
  return Math.round(Number(value)) * 100;
};

const normalizeImage = (image) => ({
  id: image?.id ?? null,
  url: image?.url || image?.image || null,
  order: image?.order ?? 0,
  is_primary: image?.is_primary ?? image?.isPrimary ?? false,
});

const normalizeVariant = (variant) => ({
  id: variant?.id ?? null,
  product_id: variant?.product_id ?? variant?.productId ?? null,
  size: variant?.size ?? '',
  price: toTenge(variant?.price),
  priceKopecks: variant?.price ?? 0,
  enabled: variant?.enabled ?? true,
});

const normalizeAddon = (addon) => ({
  id: addon?.id ?? null,
  product_id: addon?.product_id ?? addon?.productId ?? null,
  name: addon?.name ?? '',
  description: addon?.description ?? null,
  price: toTenge(addon?.price),
  priceKopecks: addon?.price ?? 0,
  is_default: addon?.is_default ?? addon?.isDefault ?? false,
  enabled: addon?.enabled ?? true,
});

/**
 * Adapt product payload from backend to internal format
 * Handles both lightweight ProductRead and extended ProductDetailRead schemas
 * @param {Object} rawProduct
 * @returns {Object|null}
 */
export function adaptProduct(rawProduct) {
  if (!rawProduct) {
    return null;
  }

  // Handle both string ("7 500 ₸") and number price formats
  const priceKopecks = typeof rawProduct.price === 'string'
    ? parsePrice(rawProduct.price)
    : (rawProduct.price ?? 0);
  const primaryImage = rawProduct.image || rawProduct.coverImage;
  const images = (rawProduct.images || [])
    .map(normalizeImage)
    .filter((img) => img.url);

  if (!images.length && primaryImage) {
    images.push(normalizeImage({ url: primaryImage, is_primary: true }));
  }

  return {
    id: rawProduct.id,
    name: rawProduct.name || rawProduct.title || '',
    price: toTenge(priceKopecks),
    priceKopecks,
    enabled: rawProduct.enabled ?? rawProduct.isAvailable ?? true,
    is_featured: rawProduct.is_featured ?? rawProduct.isFeatured ?? false,
    type: rawProduct.type || 'catalog',
    description: rawProduct.description || rawProduct.composition || '',
    manufacturing_time: rawProduct.manufacturingTime ?? rawProduct.productionTime ?? null,
    width: rawProduct.width ?? rawProduct.catalogWidth ?? null,
    height: rawProduct.height ?? rawProduct.catalogHeight ?? null,
    shelfLife: rawProduct.shelfLife ?? rawProduct.shelf_life ?? null,
    colors: rawProduct.colors || [],
    colors_detailed: rawProduct.colors_detailed || [],
    occasions: rawProduct.occasions || [],
    cities: rawProduct.cities || [],
    tags: rawProduct.tags || [],
    image: primaryImage || (images.length ? images[0].url : null),
    images,
    discount: rawProduct.discount || 0,
    video: rawProduct.video || null,
    created_at: rawProduct.created_at || rawProduct.createdAt || null,
    updated_at: rawProduct.updated_at || rawProduct.updatedAt || null,
    variants: (rawProduct.variants || []).map(normalizeVariant),
    addons: (rawProduct.addons || []).map(normalizeAddon),
    composition: rawProduct.composition || [],
    frequently_bought: (rawProduct.frequently_bought || []).map((item) => ({
      ...item,
      price: toTenge(item?.price),
      priceKopecks: item?.price ?? 0,
    })),
    pickup_locations: rawProduct.pickup_locations || [],
    reviews: rawProduct.reviews || {},
    rating: rawProduct.rating ?? null,
    review_count: rawProduct.review_count ?? 0,
    rating_count: rawProduct.rating_count ?? 0,
  };
}

/**
 * Adapt Bitrix order to internal format compatible with OrderDetail component
 * Handles both list endpoint (/orders/) and detail endpoint (/orders/detail/) formats
 * @param {Object} bitrixOrder - Order from Bitrix API v2
 * @returns {Object} - Adapted order
 */
export function adaptOrder(bitrixOrder) {

  // Detail endpoint includes legacy data in 'raw' object
  // List endpoint has flat structure
  const isDetailEndpoint = !!bitrixOrder.raw;
  const source = isDetailEndpoint ? bitrixOrder.raw : bitrixOrder;

  // Parse date from detail endpoint format "23.10.2025" or use ISO string
  let createdAt = bitrixOrder.createdAt;
  if (isDetailEndpoint && source.dateCreated) {
    // Convert "23.10.2025" to ISO format
    const parts = source.dateCreated.split('.');
    if (parts.length === 3) {
      createdAt = `${parts[2]}-${parts[1]}-${parts[0]}T00:00:00Z`;
    }
  }

  // Parse paymentAmount for list endpoint (comes as string like "65 USD" or "12 990 ₸")
  const parsePaymentAmount = (amount) => {
    if (!amount) return { price: 0, currency: 'KZT' };

    const str = amount.toString().trim();

    // Try to extract currency
    let currency = 'KZT';
    if (str.includes('USD')) {
      currency = 'USD';
    } else if (str.includes('EUR')) {
      currency = 'EUR';
    }

    // Extract numeric value
    const numericStr = str.replace(/[^0-9.,]/g, '').replace(/\s/g, '');
    const price = parseFloat(numericStr.replace(/,/g, '.')) || 0;

    return { price, currency };
  };

  const paymentInfo = parsePaymentAmount(bitrixOrder.paymentAmount);

  // Extract executors BEFORE return statement
  const executorsArray = bitrixOrder.executors || source.executors || [];

  const returnObj = {
    id: bitrixOrder.id || source.id,
    order_number: bitrixOrder.number?.toString() || source.id?.toString(),
    status: isDetailEndpoint
      ? adaptOrderStatus(source.statusId) // Detail: statusId like "AP"
      : adaptOrderStatus(bitrixOrder.status_key), // List: status_key

    // Customer (sender) info
    customer_phone: bitrixOrder.sender?.phone || source.senderPhone || bitrixOrder.phone || '',
    customer_name: bitrixOrder.sender?.name || source.senderName || '',
    sender_phone: bitrixOrder.sender?.phone || source.senderPhone || '',
    sender_name: bitrixOrder.sender?.name || source.senderName || '',
    sender_email: bitrixOrder.sender?.email || source.senderEmail || '',

    // Recipient info
    recipient_name: bitrixOrder.recipient?.name || source.recipientName || '',
    recipient_phone: bitrixOrder.recipient?.phone || source.recipientPhone || '',

    // Delivery info
    delivery_address: bitrixOrder.deliveryAddress || source.deliveryAddress || '',
    delivery_city: source.city || bitrixOrder.deliveryCity,
    delivery_time: source.deliveryType || bitrixOrder.deliveryTime,
    ask_address: bitrixOrder.askAddress || source.askAddress || false,
    is_pickup: bitrixOrder.pickup || source.pickup || false,

    // Price info - handle both detail and list endpoints
    total_price: isDetailEndpoint
      ? parseFloat(source.price) || 0 // Detail: keep as decimal for multi-currency
      : paymentInfo.price, // List: parse from paymentAmount string
    currency: isDetailEndpoint ? (source.currency || 'KZT') : paymentInfo.currency,

    // Payment info
    is_paid: isDetailEndpoint ? source.isPayed : (bitrixOrder.paymentStatus === 'Оплачен'),
    payment_method: source.paySystem || bitrixOrder.paymentStatus || '',
    payment_link: source.payLink || '',

    // Delivery details
    delivery_price: isDetailEndpoint ? parseInt(source.deliveryPrice) || 0 : 0,
    delivery_date: source.deliveryDate || bitrixOrder.deliveryDate || '',
    tracking_url: source.urls?.status || '',

    // Executors - from list endpoint executors array or detail endpoint
    florist_id: bitrixOrder.executor?.florist?.id || (bitrixOrder.executors?.[0]?.id) || 0,
    courier_id: bitrixOrder.executor?.courier?.id || 0,
    responsible_id: source.responsibleId || 0,

    // Photos
    assembled_photo: source.assembledImage || '',
    recipient_photo: source.recipientPhoto || '',

    // History
    history: bitrixOrder.history || source.history || [],

    payment_status: source.paySystem || bitrixOrder.paymentStatus,

    // Order details
    postcard_text: source.postcardText || bitrixOrder.postcardText || '',
    comment: source.comment || bitrixOrder.comment || '',
    notes: source.notes || bitrixOrder.notes || '',

    // Timestamps
    created_at: createdAt,
    updated_at: bitrixOrder.updatedAt || createdAt,

    // Images and items
    main_image: source.productImage || bitrixOrder.mainImage || '',
    executors: executorsArray,
    items: (source.basket || bitrixOrder.items || []).map(item => ({
      id: item.id,
      name: item.productName || item.name,
      quantity: item.amount || item.quantity || 1,
      price: parseFloat(item.price) || 0, // Keep as decimal, don't convert to kopecks
      currency: item.currency || 'KZT',
      image: item.productImage || item.image,
      image_big: item.productImageBig || item.image_big,
    })),
  };

  return returnObj;
}

/**
 * Convert internal product to Bitrix v2 format for API requests
 * @param {Object} product - Product in internal format
 * @returns {Object} - Bitrix API v2 format
 */
export function serializeProductForBitrix(product) {
  const payload = {
    name: product.name,
    price: toKopecks(product.price ?? product.priceTenge),
    type: product.type,
    description: product.description,
    manufacturingTime: product.manufacturing_time ?? product.manufacturingTime,
    width: product.width,
    height: product.height,
    shelfLife: product.shelfLife ?? product.shelf_life,
    enabled: product.enabled,
    is_featured: product.is_featured ?? product.isFeatured,
    colors: product.colors,
    occasions: product.occasions,
    cities: product.cities,
    tags: product.tags,
    image: product.image,
    video: product.video,
  };

  return Object.fromEntries(
    Object.entries(payload).filter(([, value]) => value !== undefined)
  );
}

/**
 * Convert internal order to Bitrix v2 format for API requests
 * @param {Object} order - Order in internal format
 * @returns {Object} - Bitrix API v2 format
 */
export function serializeOrderForBitrix(order) {
  return {
    number: order.order_number,
    status: adaptOrderStatus(order.status), // Reverse mapping
    deliveryAddressShort: order.delivery_address,
    deliveryTime: order.delivery_time,
    recipientPhoneMasked: order.customer_phone,
    recipientMasked: order.recipient_name,
  };
}

export { parsePrice, formatPrice, adaptOrderStatus, toTenge, toKopecks };
