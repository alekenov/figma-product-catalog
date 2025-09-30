/**
 * Zod Schemas for API Response Validation
 *
 * Provides runtime type safety for all API endpoints.
 * Schemas match the backend Pydantic models.
 */
import { z } from 'zod';

// ========== Product Schemas ==========

export const ProductSchema = z.object({
  id: z.number(),
  name: z.string(),
  price: z.number(), // kopecks (integer)
  type: z.enum(['flowers', 'sweets', 'fruits', 'gifts']),
  description: z.string().nullable(),
  image: z.string().nullable(),
  enabled: z.boolean(),
  is_featured: z.boolean(),
  tags: z.array(z.string()).nullable(),
  cities: z.array(z.string()).nullable(),
  manufacturingTime: z.number().nullish(),
  rating: z.number().nullish(),
  review_count: z.number().nullish(),
  rating_count: z.number().nullish(),
}).passthrough();

export const ProductImageSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  url: z.string(),
  order: z.number(),
});

export const ProductVariantSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  name: z.string(),
  price: z.number(),
  enabled: z.boolean(),
});

export const CompositionItemSchema = z.object({
  id: z.number(),
  name: z.string(),
  quantity: z.number(),
});

export const ProductAddonSchema = z.object({
  id: z.number(),
  product_id: z.number(),
  name: z.string(),
  price: z.number(),
  image: z.string().nullable(),
  enabled: z.boolean(),
});

export const ProductBundleItemSchema = z.object({
  id: z.number(),
  name: z.string(),
  price: z.number(),
  image: z.string().nullable(),
});

export const ReviewItemSchema = z.object({
  id: z.number(),
  author_name: z.string(),
  rating: z.number().min(1).max(5),
  text: z.string(),
  created_at: z.string(), // ISO datetime
});

export const ReviewAggregateSchema = z.object({
  count: z.number(),
  average_rating: z.number(),
  breakdown: z.object({
    1: z.number(),
    2: z.number(),
    3: z.number(),
    4: z.number(),
    5: z.number(),
  }),
  photos: z.array(z.string()),
  items: z.array(ReviewItemSchema),
});

export const ProductDetailSchema = z.object({
  id: z.number(),
  name: z.string(),
  price: z.number(),
  type: z.enum(['flowers', 'sweets', 'fruits', 'gifts']),
  description: z.string().nullable(),
  image: z.string().nullable(),
  enabled: z.boolean(),
  is_featured: z.boolean(),
  rating: z.number().nullable(),
  review_count: z.number().nullable(),
  rating_count: z.number().nullable(),
  images: z.array(ProductImageSchema),
  variants: z.array(ProductVariantSchema),
  composition: z.array(CompositionItemSchema),
  addons: z.array(ProductAddonSchema),
  frequently_bought: z.array(ProductBundleItemSchema),
  pickup_locations: z.array(z.string()),
  reviews: z.object({
    product: ReviewAggregateSchema,
    company: ReviewAggregateSchema,
  }),
});

export const HomeProductsSchema = z.object({
  featured: z.array(ProductSchema),
  available_tags: z.array(z.string()),
  bestsellers: z.array(ProductSchema),
});

export const FiltersSchema = z.object({
  tags: z.array(z.string()),
  cities: z.array(z.string()),
  price_range: z.object({
    min: z.number(),
    max: z.number(),
    min_tenge: z.number(),
    max_tenge: z.number(),
  }),
  product_types: z.array(z.string()),
});

// ========== Order Schemas ==========

export const OrderItemPreviewSchema = z.object({
  product_id: z.number(),
  product_name: z.string(),
  product_price: z.number(),
  quantity: z.number(),
  item_total: z.number(),
});

export const OrderPreviewSchema = z.object({
  available: z.boolean(),
  items: z.array(OrderItemPreviewSchema),
  warnings: z.array(z.string()),
  estimated_total: z.number(),
});

export const OrderItemSchema = z.object({
  id: z.number(),
  order_id: z.number(),
  product_id: z.number(),
  product_name: z.string(),
  product_price: z.number(),
  quantity: z.number(),
  item_total: z.number(),
  special_requests: z.string().nullable(),
});

export const OrderSchema = z.object({
  id: z.number(),
  orderNumber: z.string(),
  customerName: z.string(),
  phone: z.string(),
  customer_email: z.string().nullable(),
  delivery_address: z.string().nullable(),
  delivery_date: z.string().nullable(),
  delivery_notes: z.string().nullable(),
  subtotal: z.number(),
  delivery_cost: z.number(),
  total: z.number(),
  status: z.enum(['new', 'processing', 'ready', 'delivering', 'delivered', 'cancelled']),
  notes: z.string().nullable(),
  // Phase 3 fields
  recipient_name: z.string().nullable(),
  recipient_phone: z.string().nullable(),
  sender_phone: z.string().nullable(),
  pickup_address: z.string().nullable(),
  delivery_type: z.string().nullable(),
  scheduled_time: z.string().nullable(),
  payment_method: z.string().nullable(),
  order_comment: z.string().nullable(),
  bonus_points: z.number().nullable(),
  // Metadata
  created_at: z.string(),
  updated_at: z.string(),
  items: z.array(OrderItemSchema),
});

export const OrderStatusSchema = z.object({
  order_number: z.string(),
  status: z.string(),
  recipient: z.object({
    name: z.string(),
    phone: z.string().nullable(),
  }),
  delivery: z.object({
    address: z.string().nullable(),
    type: z.string().nullable(),
    scheduled_time: z.string().nullable(),
  }),
  payment: z.object({
    method: z.string().nullable(),
    total: z.number(),
  }),
  items: z.array(
    z.object({
      product_name: z.string(),
      quantity: z.number(),
      price: z.number(),
    })
  ),
  created_at: z.string(),
  updated_at: z.string(),
});

// ========== Review Schemas ==========

export const CompanyReviewsResponseSchema = z.object({
  reviews: z.array(ReviewItemSchema),
  stats: z.object({
    average_rating: z.number(),
    total_reviews: z.number(),
    rating_breakdown: z.object({
      1: z.number(),
      2: z.number(),
      3: z.number(),
      4: z.number(),
      5: z.number(),
    }),
  }),
});

// ========== FAQ Schema ==========

export const FAQSchema = z.object({
  id: z.number(),
  question: z.string(),
  answer: z.string(),
  category: z.string().nullable(),
  display_order: z.number(),
});

export const FAQsResponseSchema = z.array(FAQSchema);