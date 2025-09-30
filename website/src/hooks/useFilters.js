import { useState, useEffect } from 'react';
import { fetchFilters } from '../services/api';

/**
 * Custom hook for fetching available product filters
 *
 * @returns {{filters: Object, loading: boolean, error: string|null}}
 */
export function useFilters() {
  const [filters, setFilters] = useState({
    tags: [],
    cities: [],
    price_range: {},
    product_types: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    let abortController = new AbortController();

    async function loadFilters() {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchFilters();

        if (isMounted) {
          setFilters(data);
        }
      } catch (err) {
        if (isMounted && err.name !== 'AbortError') {
          setError(err.message);
          console.error('Error loading filters:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadFilters();

    return () => {
      isMounted = false;
      abortController.abort();
    };
  }, []); // Load once on mount

  return { filters, loading, error };
}