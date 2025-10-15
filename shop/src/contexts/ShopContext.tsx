/**
 * Shop Context
 * Provides current shop information throughout the app
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getShopFromUrl, ShopConfig } from '../utils/shopResolver';
import { fetchShopInfo, ShopInfo } from '../services/shopApi';

interface ShopContextValue {
  // Shop configuration from URL
  shopConfig: ShopConfig | null;

  // Shop information from API
  shopInfo: ShopInfo | null;

  // Loading and error states
  isLoading: boolean;
  error: Error | null;

  // Helpers
  isShopOpen: boolean;
}

const ShopContext = createContext<ShopContextValue | null>(null);

interface ShopProviderProps {
  children: ReactNode;
}

export function ShopProvider({ children }: ShopProviderProps) {
  const [shopConfig, setShopConfig] = useState<ShopConfig | null>(null);
  const [shopInfo, setShopInfo] = useState<ShopInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadShop() {
      try {
        setIsLoading(true);
        setError(null);

        // 1. Determine shop from URL
        const config = getShopFromUrl();

        if (!config) {
          throw new Error('Shop not found in URL. Please visit a valid shop page.');
        }

        setShopConfig(config);

        // 2. Fetch shop information from API
        const info = await fetchShopInfo(config.id);
        setShopInfo(info);

      } catch (err) {
        console.error('[ShopContext] Failed to load shop:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    }

    loadShop();
  }, []);

  // Calculate if shop is open
  const isShopOpen = shopInfo ? calculateIsOpen(shopInfo) : false;

  const value: ShopContextValue = {
    shopConfig,
    shopInfo,
    isLoading,
    error,
    isShopOpen,
  };

  // Show error state
  if (error && !isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Магазин не найден
          </h2>
          <p className="text-gray-600 mb-4">
            {error.message}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка магазина...</p>
        </div>
      </div>
    );
  }

  return (
    <ShopContext.Provider value={value}>
      {children}
    </ShopContext.Provider>
  );
}

/**
 * Hook to access shop context
 */
export function useShop(): ShopContextValue {
  const context = useContext(ShopContext);

  if (!context) {
    throw new Error('useShop must be used within ShopProvider');
  }

  return context;
}

/**
 * Calculate if shop is currently open
 */
function calculateIsOpen(shop: ShopInfo): boolean {
  const now = new Date();
  const currentDay = now.getDay(); // 0 = Sunday, 6 = Saturday
  const isWeekend = currentDay === 0 || currentDay === 6;
  const currentTime = now.toTimeString().slice(0, 5); // HH:MM format

  if (isWeekend) {
    if (shop.weekend_closed) return false;
    return currentTime >= shop.weekend_start && currentTime <= shop.weekend_end;
  } else {
    if (shop.weekday_closed) return false;
    return currentTime >= shop.weekday_start && currentTime <= shop.weekday_end;
  }
}
