/**
 * TypeScript Type Definitions for Bitrix API v2
 *
 * This file provides type definitions for the Flower Shop CRM API
 * Used for autocomplete and type checking in JavaScript projects
 *
 * @version 2.0
 * @date 2025-10-25
 */

// ============================================================================
// ORDER TYPES
// ============================================================================

/**
 * Order status enumeration
 * Represents the current state of an order in the fulfillment workflow
 */
export type OrderStatus =
  | 'NEW'           // New order, awaiting payment
  | 'PAID'          // Payment confirmed
  | 'ACCEPTED'      // Order accepted by florist
  | 'IN_PRODUCTION' // Being assembled (also called "ASSEMBLED")
  | 'IN_DELIVERY'   // En route to recipient
  | 'DELIVERED'     // Successfully delivered
  | 'CANCELLED';    // Order cancelled

/**
 * Lowercase version of order status (used in API filters)
 */
export type OrderStatusLower =
  | 'new'
  | 'paid'
  | 'accepted'
  | 'assembled'
  | 'in_delivery'
  | 'delivered'
  | 'cancelled';

/**
 * Payment method/status indicator
 */
export type PaymentMethod =
  | 'Оплачен'      // Paid
  | 'Не оплачен'   // Not paid
  | 'Kaspi Pay'    // Kaspi Pay payment system
  | 'Наличные'     // Cash
  | 'Терминал';    // Card terminal

/**
 * Delivery method type
 */
export type DeliveryMethod =
  | 'Доставка'    // Delivery to address
  | 'Самовывоз';  // Pickup from location

/**
 * Currency code
 */
export type Currency = 'KZT' | 'USD' | 'EUR';

/**
 * Recipient information
 * Contains details about the person receiving the order
 */
export interface Recipient {
  /** Recipient full name (may be null if "ask recipient" is checked) */
  name: string | null;
  /** Recipient phone number in format +7XXXXXXXXXX (may be null) */
  phone: string | null;
}

/**
 * Sender information
 * Contains details about the person placing the order
 */
export interface Sender {
  /** Sender full name */
  name: string;
  /** Sender phone number in format +7XXXXXXXXXX */
  phone: string;
  /** Sender email address (optional) */
  email?: string;
}

/**
 * Executor information
 * Represents a person assigned to work on the order (florist, courier, etc.)
 */
export interface Executor {
  /** User ID in the system */
  id: string;
  /** Full name of the executor */
  name: string;
  /** Avatar URL (nullable if no avatar uploaded) */
  avatar: string | null;
  /** Source system or role (e.g., "Cvety.kz", "Florist", "Courier") */
  source: string;
}

/**
 * Order item
 * Represents a single product in the order basket
 */
export interface OrderItem {
  /** Item ID */
  id: number;
  /** Product name */
  name: string;
  /** Product description (optional) */
  description?: string;
  /** Quantity ordered */
  quantity: number;
  /** Formatted price with currency (e.g., "12 990 ₸") */
  price: string;
  /** Raw price value (decimal number, not kopecks) */
  priceRaw: number;
  /** Total price for this item (price * quantity) */
  total: number;
  /** Currency code */
  currency: Currency;
  /** Product image URL (main image or thumbnail) */
  image: string;
  /** Product image (large version) */
  image_big?: string;
  /** Special customer requests for this item */
  special_requests?: string;
}

/**
 * Order photo
 * Represents photos attached to the order (assembled bouquet, delivery confirmation, etc.)
 */
export interface OrderPhoto {
  /** Full image URL */
  url: string;
  /** Photo label/description (e.g., "Assembled bouquet", "Delivered") */
  label: string;
  /** Photo type identifier (e.g., "assembled", "delivered") */
  type: string;
  /** Client feedback on this photo (optional) */
  feedback?: string;
  /** Client comment on this photo (optional) */
  comment?: string;
}

/**
 * Order history entry
 * Tracks status changes and important events in order lifecycle
 */
export interface OrderHistoryEntry {
  /** Timestamp when this event occurred (ISO 8601 format) */
  timestamp: string;
  /** Previous order status */
  from_status?: OrderStatus;
  /** New order status */
  to_status: OrderStatus;
  /** User who performed this action */
  user_id?: number;
  /** User name who performed this action */
  user_name?: string;
  /** Additional notes about this change */
  notes?: string;
}

/**
 * Single order item in list response
 * Represents an order in the list view with essential information
 */
export interface OrderListItem {
  /** Unique order ID */
  id: number;

  /** Tracking ID for public order tracking (UUID format) */
  tracking_id?: string;

  /** Human-readable order number (e.g., "#12345") */
  orderNumber: string;

  /** Current order status (lowercase for UI filters) */
  status: OrderStatusLower;

  /** Localized status label (e.g., "Новый", "Оплачен", "Принят") */
  statusLabel: string;

  /** Customer/recipient display name */
  customerName: string;

  /** Customer phone number */
  phone: string;

  /** Customer email (optional) */
  customer_email?: string;

  /** Formatted total price with currency (e.g., "12 990 ₸") */
  total: string;

  /** Raw total price value for calculations */
  totalRaw: number;

  /** Currency code */
  currency: Currency;

  /** Relative time when order was created (e.g., "2 часа назад") */
  createdAt: string;

  /** Detailed creation timestamp (e.g., "24 октября в 15:46") */
  createdAtDetailed: string;

  /**
   * Delivery address or pickup location
   * Special values:
   * - "Самовывоз" = Pickup
   * - "Уточнить у получателя" = Ask recipient
   * - "Адрес не указан" = No address provided
   */
  delivery_address: string;

  /**
   * Delivery date and time in human-readable format
   * Examples: "сегодня в 14:00", "завтра в 10:00", "26 октября"
   */
  delivery_date: string;

  /** Raw delivery date (ISO 8601 format) for editing */
  delivery_date_raw?: string;

  /** Delivery time window (e.g., "13:00-14:00") */
  delivery_time?: string;

  /** Main product image URL (first item image) */
  mainImage: string;

  /**
   * Array of all product images from order items
   * Used for overlapping image display in order cards
   */
  itemImages: string[];

  /**
   * Formatted payment amount with currency
   * Example: "12 990 ₸" or "65 USD"
   */
  paymentAmount?: string;

  /** Payment method/status */
  payment_method?: PaymentMethod;

  /** Whether order has been paid */
  is_paid: boolean;

  /**
   * Array of executors assigned to this order
   * Includes florists, couriers, and managers
   */
  executors: Executor[];

  /** Sender information */
  sender_name?: string;
  sender_phone?: string;
  sender_email?: string;

  /** Recipient information */
  recipient_name?: string;
  recipient_phone?: string;

  /** Order items (products in basket) */
  items: OrderItem[];

  /** Delivery notes/instructions */
  delivery_notes?: string;

  /** Internal notes (admin only) */
  notes?: string;

  /** Postcard message text */
  postcard_text?: string;

  /** Customer comment/special requests */
  comment?: string;

  /** Delivery price (raw number, not formatted) */
  delivery_price?: number;

  /** Photos attached to order (assembled, delivered, etc.) */
  photos: OrderPhoto[];

  /** Assembled bouquet photo URL */
  assembled_photo?: string;

  /** Delivery confirmation photo URL */
  recipient_photo?: string;

  /** Order status change history */
  history: OrderHistoryEntry[];

  /** Kaspi Pay payment ID (if paid via Kaspi) */
  kaspi_payment_id?: string;

  /** Kaspi Pay payment status */
  kaspi_payment_status?: string;

  /** Kaspi Pay payment creation timestamp */
  kaspi_payment_created_at?: string;

  /** Kaspi Pay payment completion timestamp */
  kaspi_payment_completed_at?: string;

  /** User ID of assigned florist/manager */
  assigned_to?: number;

  /** Name of assigned florist/manager */
  assigned_to_name?: string;

  /** User ID of assigned courier */
  courier?: number;

  /** Name of assigned courier */
  courier_name?: string;
}

/**
 * Pagination metadata
 * Contains information about result set pagination
 */
export interface Pagination {
  /** Total number of items across all pages */
  total: number;

  /** Whether there are more items to load */
  has_more: boolean;

  /** Number of items per page */
  limit: number;

  /** Offset from start of result set */
  offset: number;
}

/**
 * Order list response from GET /api/v2/orders/
 * Contains array of orders and pagination metadata
 */
export interface OrderListResponse {
  /** Array of orders */
  orders: OrderListItem[];

  /** Pagination information */
  pagination: Pagination;
}

/**
 * Order detail response from GET /api/v2/orders/detail/?id={orderId}
 * Contains full order information including all nested data
 *
 * Note: This extends OrderListItem with all the same fields
 * The detail endpoint returns more complete information (e.g., full history)
 */
export type OrderDetailResponse = OrderListItem;

// ============================================================================
// API ERROR TYPES
// ============================================================================

/**
 * Standardized API error response
 * Returned when API request fails
 */
export interface ApiError {
  /** Error type/code (e.g., "NOT_FOUND", "VALIDATION_ERROR") */
  error: string;

  /** Human-readable error message */
  message: string;

  /** HTTP status code */
  status: number;

  /** Additional error details (optional) */
  details?: Record<string, any>;

  /** Field-specific validation errors (optional) */
  field_errors?: Record<string, string[]>;
}

// ============================================================================
// API REQUEST TYPES
// ============================================================================

/**
 * Query parameters for GET /api/v2/orders/
 */
export interface OrderListParams {
  /** Pagination offset (number of items to skip) */
  offset?: number;

  /** Maximum number of items to return (default: 20) */
  limit?: number;

  /** Filter by order status (lowercase) */
  status?: OrderStatusLower | 'all';

  /** Search query (searches in order number, customer name, phone) */
  search?: string;

  /** Filter by customer phone */
  customer_phone?: string;
}

/**
 * Request body for PATCH /api/v2/orders/{orderId}/status/
 */
export interface OrderStatusUpdateRequest {
  /** New order status */
  status: OrderStatus;

  /** Optional notes about status change */
  notes?: string;
}

/**
 * Request body for POST /api/v2/orders/ (create order)
 */
export interface CreateOrderRequest {
  /** Order items (product IDs and quantities) */
  items: Array<{
    product_id: number;
    quantity: number;
  }>;

  /** Customer phone number */
  phone: string;

  /** Customer name */
  customer_name: string;

  /** Recipient name (for delivery orders) */
  recipient_name?: string;

  /** Recipient phone (for delivery orders) */
  recipient_phone?: string;

  /** Delivery address (required unless pickup or ask_address) */
  delivery_address?: string;

  /** Delivery date (ISO 8601 format or simple date) */
  delivery_date: string;

  /** Delivery time window (e.g., "13:00-14:00") */
  delivery_time: string;

  /** Delivery type ("delivery" or "pickup") */
  delivery_type: 'delivery' | 'pickup';

  /** Pickup location ID (if pickup) */
  pickup_location_id?: number;

  /** Ask recipient for address flag */
  ask_address?: boolean;

  /** Postcard message text */
  postcard_text?: string;

  /** Customer comment/special requests */
  comment?: string;

  /** Total order price in kopecks */
  total_price: number;

  /** Delivery cost in kopecks */
  delivery_cost?: number;

  /** Shop ID (multi-tenancy) */
  shop_id: number;
}

// ============================================================================
// PRODUCT TYPES (for reference in orders)
// ============================================================================

/**
 * Product type enumeration
 */
export type ProductType =
  | 'catalog'       // Regular catalog item
  | 'ready'         // Ready-made bouquet
  | 'constructor';  // Custom bouquet constructor

/**
 * Product information (minimal, as referenced in orders)
 */
export interface Product {
  /** Product ID */
  id: number;

  /** Product name */
  name: string;

  /** Price in kopecks */
  price: number;

  /** Product type */
  type: ProductType;

  /** Product image URL */
  image: string;

  /** Whether product is enabled/available */
  enabled: boolean;

  /** Whether product is featured */
  is_featured: boolean;
}

// ============================================================================
// USER TYPES
// ============================================================================

/**
 * User role enumeration
 */
export type UserRole =
  | 'DIRECTOR'   // Shop owner/director
  | 'MANAGER'    // Store manager
  | 'WORKER'     // Florist/staff
  | 'COURIER';   // Delivery courier

/**
 * User information
 */
export interface User {
  /** User ID */
  id: number;

  /** User phone number */
  phone: string;

  /** User full name */
  name: string;

  /** User email (optional) */
  email?: string;

  /** User role */
  role: UserRole;

  /** Shop ID this user belongs to */
  shop_id: number;

  /** Avatar URL (optional) */
  avatar?: string;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * API response wrapper (generic)
 * Some endpoints wrap data in a data field
 */
export interface ApiResponse<T> {
  /** Response data */
  data: T;

  /** Success status */
  success?: boolean;

  /** Response message (optional) */
  message?: string;
}

/**
 * Empty response (for successful operations with no return data)
 */
export interface EmptyResponse {
  /** Success status */
  success: boolean;

  /** Optional message */
  message?: string;
}

// ============================================================================
// EXPORTS
// ============================================================================

export {
  OrderListItem,
  OrderListResponse,
  OrderDetailResponse,
  OrderListParams,
  OrderStatusUpdateRequest,
  CreateOrderRequest,
  Pagination,
  ApiError,
  Recipient,
  Sender,
  Executor,
  OrderItem,
  OrderPhoto,
  OrderHistoryEntry,
  OrderStatus,
  OrderStatusLower,
  PaymentMethod,
  DeliveryMethod,
  Currency,
  Product,
  ProductType,
  User,
  UserRole,
  ApiResponse,
  EmptyResponse,
};
