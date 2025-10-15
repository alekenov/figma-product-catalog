/**
 * Cart Context
 * Manages shopping cart state with localStorage persistence
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useShop } from './ShopContext';

// ============================================================================
// Types
// ============================================================================

export interface CartItem {
  product_id: number;
  product_name: string;
  product_price: number; // in kopecks
  quantity: number;
  image?: string;
  special_requests?: string;
}

interface CartContextValue {
  // Cart state
  items: CartItem[];
  itemCount: number;

  // Calculations (all in kopecks)
  subtotal: number;
  deliveryCost: number;
  total: number;

  // Methods
  addToCart: (product: { id: number; name: string; price: number; image?: string }) => void;
  removeFromCart: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  updateSpecialRequests: (productId: number, requests: string) => void;
  clearCart: () => void;

  // Delivery
  deliveryMethod: 'delivery' | 'pickup';
  setDeliveryMethod: (method: 'delivery' | 'pickup') => void;
}

const CartContext = createContext<CartContextValue | null>(null);

// ============================================================================
// Provider
// ============================================================================

interface CartProviderProps {
  children: ReactNode;
}

export function CartProvider({ children }: CartProviderProps) {
  const { shopConfig, shopInfo } = useShop();
  const [items, setItems] = useState<CartItem[]>([]);
  const [deliveryMethod, setDeliveryMethod] = useState<'delivery' | 'pickup'>('delivery');

  // Load cart from localStorage on mount
  useEffect(() => {
    if (!shopConfig) return;

    const storageKey = `cart_${shopConfig.id}`;
    const savedCart = localStorage.getItem(storageKey);

    if (savedCart) {
      try {
        const parsed = JSON.parse(savedCart);
        setItems(parsed.items || []);
        setDeliveryMethod(parsed.deliveryMethod || 'delivery');
      } catch (error) {
        console.error('[CartContext] Failed to parse saved cart:', error);
      }
    }
  }, [shopConfig]);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    if (!shopConfig) return;

    const storageKey = `cart_${shopConfig.id}`;
    localStorage.setItem(storageKey, JSON.stringify({
      items,
      deliveryMethod,
      timestamp: new Date().toISOString()
    }));
  }, [items, deliveryMethod, shopConfig]);

  // ============================================================================
  // Calculations
  // ============================================================================

  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  const subtotal = items.reduce((sum, item) => sum + item.product_price * item.quantity, 0);

  const deliveryCost = (() => {
    if (deliveryMethod === 'pickup') return 0;
    if (!shopInfo) return 0;

    // Check free delivery threshold
    const subtotalInKopecks = subtotal;
    const freeDeliveryThresholdKopecks = (shopInfo.free_delivery_amount_tenge || 0) * 100;

    if (subtotalInKopecks >= freeDeliveryThresholdKopecks && freeDeliveryThresholdKopecks > 0) {
      return 0; // Free delivery
    }

    return shopInfo.delivery_cost_tenge * 100; // Convert tenge to kopecks
  })();

  const total = subtotal + deliveryCost;

  // ============================================================================
  // Methods
  // ============================================================================

  const addToCart = (product: { id: number; name: string; price: number; image?: string }) => {
    setItems(currentItems => {
      const existingItem = currentItems.find(item => item.product_id === product.id);

      if (existingItem) {
        // Increment quantity
        return currentItems.map(item =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        // Add new item
        return [
          ...currentItems,
          {
            product_id: product.id,
            product_name: product.name,
            product_price: product.price,
            quantity: 1,
            image: product.image,
          }
        ];
      }
    });
  };

  const removeFromCart = (productId: number) => {
    setItems(currentItems => currentItems.filter(item => item.product_id !== productId));
  };

  const updateQuantity = (productId: number, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setItems(currentItems =>
      currentItems.map(item =>
        item.product_id === productId
          ? { ...item, quantity }
          : item
      )
    );
  };

  const updateSpecialRequests = (productId: number, requests: string) => {
    setItems(currentItems =>
      currentItems.map(item =>
        item.product_id === productId
          ? { ...item, special_requests: requests }
          : item
      )
    );
  };

  const clearCart = () => {
    setItems([]);
    if (shopConfig) {
      const storageKey = `cart_${shopConfig.id}`;
      localStorage.removeItem(storageKey);
    }
  };

  // ============================================================================
  // Context Value
  // ============================================================================

  const value: CartContextValue = {
    items,
    itemCount,
    subtotal,
    deliveryCost,
    total,
    addToCart,
    removeFromCart,
    updateQuantity,
    updateSpecialRequests,
    clearCart,
    deliveryMethod,
    setDeliveryMethod,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

/**
 * Hook to access cart context
 */
export function useCart(): CartContextValue {
  const context = useContext(CartContext);

  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }

  return context;
}
