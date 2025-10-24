import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock OrderContext - MUST be before imports
let mockOrderData = {
  items: [
    {
      name: 'Букет роз "Нежность"',
      description: '15 красных роз премиум класса',
      quantity: 2,
      price: '15 000 ₸',
      total: '30 000 ₸',
      special_requests: 'Добавить открытку'
    },
    {
      name: 'Плюшевый мишка',
      description: null,
      quantity: 1,
      price: '5 000 ₸',
      total: '5 000 ₸',
      special_requests: null
    }
  ],
  subtotal: '35 000 ₸',
  delivery_cost: '1 500 ₸',
  total: '36 500 ₸'
};

vi.mock('./OrderContext', () => ({
  useOrder: () => ({ orderData: mockOrderData })
}));

import OrderItemsList from './OrderItemsList';

describe('OrderItemsList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset mock data to default
    mockOrderData = {
      items: [
        {
          name: 'Букет роз "Нежность"',
          description: '15 красных роз премиум класса',
          quantity: 2,
          price: '15 000 ₸',
          total: '30 000 ₸',
          special_requests: 'Добавить открытку'
        },
        {
          name: 'Плюшевый мишка',
          description: null,
          quantity: 1,
          price: '5 000 ₸',
          total: '5 000 ₸',
          special_requests: null
        }
      ],
      subtotal: '35 000 ₸',
      delivery_cost: '1 500 ₸',
      total: '36 500 ₸'
    };
  });

  it('should render items table header', () => {
    render(<OrderItemsList />);

    expect(screen.getByText('Товары')).toBeInTheDocument();
    expect(screen.getByText('Товар')).toBeInTheDocument();
    expect(screen.getByText('Кол-во')).toBeInTheDocument();
    expect(screen.getByText('Цена')).toBeInTheDocument();
    expect(screen.getByText('Сумма')).toBeInTheDocument();
  });

  it('should render all items with details', () => {
    render(<OrderItemsList />);

    expect(screen.getByText('Букет роз "Нежность"')).toBeInTheDocument();
    expect(screen.getByText('15 красных роз премиум класса')).toBeInTheDocument();
    expect(screen.getByText('Плюшевый мишка')).toBeInTheDocument();
  });

  it('should display item quantities correctly', () => {
    render(<OrderItemsList />);

    const rows = screen.getAllByRole('row');
    // Header + 2 items = 3 rows in tbody
    expect(rows.length).toBeGreaterThan(2);
  });

  it('should display prices and totals', () => {
    render(<OrderItemsList />);

    expect(screen.getAllByText('15 000 ₸').length).toBeGreaterThan(0);
    expect(screen.getByText('30 000 ₸')).toBeInTheDocument();
    expect(screen.getByText('5 000 ₸')).toBeInTheDocument();
  });

  it('should display special requests when available', () => {
    render(<OrderItemsList />);

    expect(screen.getByText(/Примечание: Добавить открытку/)).toBeInTheDocument();
  });

  it('should not display special requests when not available', () => {
    render(<OrderItemsList />);

    const specialRequestsElements = screen.queryAllByText(/Примечание:/);
    // Should only have one (for the first item)
    expect(specialRequestsElements).toHaveLength(1);
  });

  it('should display subtotal', () => {
    render(<OrderItemsList />);

    expect(screen.getByText('Подытог:')).toBeInTheDocument();
    expect(screen.getByText('35 000 ₸')).toBeInTheDocument();
  });

  it('should display delivery cost when available', () => {
    render(<OrderItemsList />);

    expect(screen.getByText('Доставка:')).toBeInTheDocument();
    expect(screen.getByText('1 500 ₸')).toBeInTheDocument();
  });

  it('should not display delivery cost when zero', () => {
    mockOrderData = {
      ...mockOrderData,
      delivery_cost: '0 ₸'
    };
    render(<OrderItemsList />);

    expect(screen.queryByText('Доставка:')).not.toBeInTheDocument();
  });

  it('should display total amount', () => {
    render(<OrderItemsList />);

    expect(screen.getByText('Итого:')).toBeInTheDocument();
    expect(screen.getByText('36 500 ₸')).toBeInTheDocument();
  });

  it('should return null when orderData is not available', () => {
    mockOrderData = null;
    const { container } = render(<OrderItemsList />);

    expect(container.firstChild).toBeNull();
  });

  it('should return null when items array is empty', () => {
    mockOrderData = {
      ...mockOrderData,
      items: []
    };
    const { container } = render(<OrderItemsList />);

    expect(container.firstChild).toBeNull();
  });

  it('should return null when items is null', () => {
    mockOrderData = {
      ...mockOrderData,
      items: null
    };
    const { container } = render(<OrderItemsList />);

    expect(container.firstChild).toBeNull();
  });

  it('should handle items without description', () => {
    render(<OrderItemsList />);

    // Second item has no description, should still render
    expect(screen.getByText('Плюшевый мишка')).toBeInTheDocument();

    // Should not have a description element for this item
    const plushToyRow = screen.getByText('Плюшевый мишка').closest('tr');
    expect(plushToyRow?.textContent).not.toContain('15 красных роз');
  });

  it('should style total amount with purple color', () => {
    const { container } = render(<OrderItemsList />);

    const totalCell = container.querySelector('.text-purple-primary');
    expect(totalCell).toBeInTheDocument();
    expect(totalCell?.textContent).toBe('36 500 ₸');
  });

  it('should apply bold styling to subtotal and total', () => {
    const { container } = render(<OrderItemsList />);

    const boldElements = container.querySelectorAll('.font-bold');
    expect(boldElements.length).toBeGreaterThan(0);
  });
});
