import { useState, useEffect } from 'react';
import { fetchHomeProducts } from '../services/api';

/**
 * Custom hook for fetching home products with optional filters
 *
 * @param {string|null} city - City filter (e.g., "almaty", "astana")
 * @param {Array<string>} tags - Array of active tag filters
 * @returns {{products: Array, loading: boolean, error: string|null, refetch: Function}}
 */
export function useHomeProducts(city = null, tags = []) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refetchCounter, setRefetchCounter] = useState(0);

  useEffect(() => {
    let isMounted = true;
    let abortController = new AbortController();

    async function loadProducts() {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchHomeProducts(city, tags);

        if (isMounted) {
          setProducts(data.featured || []);
        }
      } catch (err) {
        if (isMounted && err.name !== 'AbortError') {
          setError(err.message);
          console.error('Error loading products:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadProducts();

    return () => {
      isMounted = false;
      abortController.abort();
    };
  }, [city, tags.join(','), refetchCounter]); // Refetch when filters change

  // Manual refetch function
  const refetch = () => {
    setRefetchCounter(prev => prev + 1);
  };

  return { products, loading, error, refetch };
}