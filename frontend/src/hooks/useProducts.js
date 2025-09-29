import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productsAPI, formatProductForDisplay } from '../services/api';
import placeholderImage from '../assets/placeholder.svg';

// Query key factory for products
export const productKeys = {
  all: ['products'],
  lists: () => [...productKeys.all, 'list'],
  list: (filters) => [...productKeys.lists(), { filters }],
  details: () => [...productKeys.all, 'detail'],
  detail: (id) => [...productKeys.details(), id],
};

// Hook to fetch all products with caching
export const useProducts = (options = {}) => {
  return useQuery({
    queryKey: productKeys.list(options),
    queryFn: async () => {
      const rawProducts = await productsAPI.getProducts({
        limit: 100,
        enabled_only: false,
        ...options
      });

      // Format products for display
      return rawProducts.map(product => {
        const formatted = formatProductForDisplay(product);
        return {
          ...formatted,
          price: `${formatted.price.toLocaleString()} ₸`,
          image: product.image || placeholderImage // Fallback image
        };
      });
    },
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  });
};

// Hook to fetch a single product
export const useProduct = (id) => {
  return useQuery({
    queryKey: productKeys.detail(id),
    queryFn: () => productsAPI.getProduct(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook to update product
export const useUpdateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => productsAPI.updateProduct(id, data),
    onSuccess: (data, variables) => {
      // Invalidate and refetch products list
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      // Update the specific product in cache
      queryClient.setQueryData(productKeys.detail(variables.id), data);
    },
  });
};

// Hook to create product
export const useCreateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => productsAPI.createProduct(data),
    onSuccess: () => {
      // Invalidate products list to refetch with new product
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
};

// Hook to delete product
export const useDeleteProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) => productsAPI.deleteProduct(id),
    onSuccess: (_, id) => {
      // Invalidate products list
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      // Remove from cache
      queryClient.removeQueries({ queryKey: productKeys.detail(id) });
    },
  });
};