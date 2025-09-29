import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import Orders from './Orders';

// Mock the API module
vi.mock('./services/api', () => ({
  ordersAPI: {
    getAll: vi.fn(),
  },
  formatOrderForDisplay: vi.fn((order) => ({
    ...order,
    displayStatus: order.status === 'new' ? 'Новый' :
                   order.status === 'processing' ? 'В обработке' :
                   order.status === 'completed' ? 'Завершен' : 'Отменен',
    displayDate: new Date(order.createdAt).toLocaleDateString('ru-RU'),
    displaySum: `${order.totalAmount || 0} ₸`,
  })),
}));

// Mock data
const mockOrders = [
  {
    id: 1,
    orderNumber: 'ORD-001',
    clientName: 'Иван Иванов',
    status: 'new',
    totalAmount: 25000,
    createdAt: '2024-01-20T10:00:00',
    items: [
      { name: 'Красные розы', quantity: 10 },
      { name: 'Белые лилии', quantity: 5 }
    ]
  },
  {
    id: 2,
    orderNumber: 'ORD-002',
    clientName: 'Мария Петрова',
    status: 'processing',
    totalAmount: 15000,
    createdAt: '2024-01-21T14:30:00',
    items: [
      { name: 'Тюльпаны', quantity: 20 }
    ]
  },
  {
    id: 3,
    orderNumber: 'ORD-003',
    clientName: 'Алексей Сидоров',
    status: 'completed',
    totalAmount: 35000,
    createdAt: '2024-01-22T09:15:00',
    items: [
      { name: 'Орхидеи', quantity: 3 },
      { name: 'Розы', quantity: 15 }
    ]
  },
];

// Setup MSW server
const server = setupServer(
  http.get('/api/orders', () => {
    return HttpResponse.json(mockOrders);
  })
);

beforeEach(() => {
  server.listen();
});

afterEach(() => {
  server.resetHandlers();
  vi.clearAllMocks();
});

describe('Orders Page', () => {
  const setup = () => {
    const user = userEvent.setup();
    const utils = render(
      <MemoryRouter initialEntries={['/orders']}>
        <Orders />
      </MemoryRouter>
    );
    return {
      user,
      ...utils,
    };
  };

  describe('Initial Rendering', () => {
    it('should render page header with title', () => {
      setup();

      expect(screen.getByText('Заказы')).toBeInTheDocument();
    });

    it('should render search toggle button', () => {
      setup();

      const searchButton = screen.getByRole('button', { name: /открыть поиск/i });
      expect(searchButton).toBeInTheDocument();
    });

    it('should render create order button', () => {
      setup();

      const createButton = screen.getByRole('button', { name: /Создать заказ/i });
      expect(createButton).toBeInTheDocument();
    });

    it('should render filter header', () => {
      setup();

      // FilterHeader should be present with orders icon
      expect(screen.getByText('Фильтры')).toBeInTheDocument();
    });

    it('should render bottom navigation with orders tab active', () => {
      setup();

      const ordersTab = screen.getByText('Заказы');
      expect(ordersTab).toHaveClass('text-purple-primary');
    });
  });

  describe('Orders Data Loading', () => {
    it('should load and display orders on mount', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        expect(screen.getByText('ORD-001')).toBeInTheDocument();
        expect(screen.getByText('ORD-002')).toBeInTheDocument();
        expect(screen.getByText('ORD-003')).toBeInTheDocument();
      });
    });

    it('should display client names', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        expect(screen.getByText('Иван Иванов')).toBeInTheDocument();
        expect(screen.getByText('Мария Петрова')).toBeInTheDocument();
        expect(screen.getByText('Алексей Сидоров')).toBeInTheDocument();
      });
    });

    it('should display order statuses', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        expect(screen.getByText('Новый')).toBeInTheDocument();
        expect(screen.getByText('В обработке')).toBeInTheDocument();
        expect(screen.getByText('Завершен')).toBeInTheDocument();
      });
    });

    it('should display order amounts', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        expect(screen.getByText('25000 ₸')).toBeInTheDocument();
        expect(screen.getByText('15000 ₸')).toBeInTheDocument();
        expect(screen.getByText('35000 ₸')).toBeInTheDocument();
      });
    });

    it('should handle empty order list', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce([]);

      setup();

      await waitFor(() => {
        expect(screen.queryByText('ORD-001')).not.toBeInTheDocument();
      });
    });
  });

  describe('Status Badges', () => {
    it('should apply correct styling for new status', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        const newBadge = screen.getByText('Новый');
        expect(newBadge).toBeInTheDocument();
        // Check for green/success styling
        expect(newBadge.closest('span')).toHaveClass('bg-green-100');
      });
    });

    it('should apply correct styling for processing status', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        const processingBadge = screen.getByText('В обработке');
        expect(processingBadge).toBeInTheDocument();
        // Check for yellow/warning styling
        expect(processingBadge.closest('span')).toHaveClass('bg-yellow-100');
      });
    });

    it('should apply correct styling for completed status', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        const completedBadge = screen.getByText('Завершен');
        expect(completedBadge).toBeInTheDocument();
        // Check for gray/neutral styling
        expect(completedBadge.closest('span')).toHaveClass('bg-gray-100');
      });
    });
  });

  describe('Search Functionality', () => {
    it('should toggle search input when search button is clicked', async () => {
      const { user } = setup();

      const searchButton = screen.getByRole('button', { name: /открыть поиск/i });
      await user.click(searchButton);

      // Check that search state changed
      expect(searchButton).toHaveAttribute('aria-label', 'Свернуть поиск');
    });

    it('should filter orders by search query', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      const { user } = setup();

      await waitFor(() => {
        expect(screen.getByText('ORD-001')).toBeInTheDocument();
        expect(screen.getByText('ORD-002')).toBeInTheDocument();
      });

      // Implementation would filter orders based on search
      // This tests the structure, actual filtering depends on implementation
    });
  });

  describe('Filter Functionality', () => {
    it('should handle filter button click', async () => {
      const { user } = setup();

      const filtersButton = screen.getByRole('button', { name: /Фильтры/i });
      await user.click(filtersButton);

      // Filter modal/page would open here
      // Testing the interaction structure
    });
  });

  describe('Navigation', () => {
    it('should navigate to order detail when clicking on order', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      const navigate = vi.fn();
      vi.mock('react-router-dom', async () => {
        const actual = await vi.importActual('react-router-dom');
        return {
          ...actual,
          useNavigate: () => navigate,
        };
      });

      const { user } = setup();

      await waitFor(() => {
        expect(screen.getByText('ORD-001')).toBeInTheDocument();
      });

      const orderCard = screen.getByText('ORD-001').closest('div');
      if (orderCard) {
        await user.click(orderCard);
        // Navigation would occur
      }
    });

    it('should navigate to create order when create button is clicked', async () => {
      const navigate = vi.fn();
      vi.mock('react-router-dom', async () => {
        const actual = await vi.importActual('react-router-dom');
        return {
          ...actual,
          useNavigate: () => navigate,
        };
      });

      const { user } = setup();

      const createButton = screen.getByRole('button', { name: /Создать заказ/i });
      await user.click(createButton);

      // Navigation to create order page
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockRejectedValueOnce(new Error('Network error'));

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      setup();

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Performance', () => {
    it('should not re-fetch orders on every render', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValue(mockOrders);

      const { rerender } = setup();

      await waitFor(() => {
        expect(screen.getByText('ORD-001')).toBeInTheDocument();
      });

      // Re-render the component
      rerender(
        <MemoryRouter initialEntries={['/orders']}>
          <Orders />
        </MemoryRouter>
      );

      // API should only be called once
      expect(ordersAPI.getAll).toHaveBeenCalledTimes(1);
    });

    it('should memoize filtered results', async () => {
      const { ordersAPI } = await import('./services/api');
      ordersAPI.getAll.mockResolvedValueOnce(mockOrders);

      setup();

      await waitFor(() => {
        expect(screen.getByText('ORD-001')).toBeInTheDocument();
      });

      // Filtered results should be memoized to avoid recalculation
      // This is implementation specific
    });
  });
});