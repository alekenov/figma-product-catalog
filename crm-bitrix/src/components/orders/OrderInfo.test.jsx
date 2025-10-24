import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Mock OrderContext - MUST be before imports
let mockOrderData = {
  orderNumber: 'ORD-12345',
  tracking_id: 'TRK-ABC123',
  created_at: '2025-10-20T10:30:00',
  customerName: 'John Doe',
  phone: '+77001234567',
  delivery_type: 'delivery',
  delivery_address: 'ул. Абая 150, кв. 25',
  delivery_date: '2025-10-25',
  delivery_time: '14:00-16:00',
  payment_method: 'kaspi',
  notes: 'Пожалуйста, позвоните за 30 минут'
};

let mockRecipientInfo = {
  name: 'Jane Smith',
  phone: '+77009876543'
};

vi.mock('./OrderContext', () => ({
  useOrder: () => ({
    orderData: mockOrderData,
    recipientInfo: mockRecipientInfo
  })
}));

// Mock InfoRow component
vi.mock('../InfoRow', () => ({
  default: ({ label, value, action }) => (
    <div data-testid="info-row">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
      {action && <div className="action">{action}</div>}
    </div>
  )
}));

import OrderInfo from './OrderInfo';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn()
  }
});

// Mock window.alert
global.alert = vi.fn();

describe('OrderInfo', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset mock data to default
    mockOrderData = {
      orderNumber: 'ORD-12345',
      tracking_id: 'TRK-ABC123',
      created_at: '2025-10-20T10:30:00',
      customerName: 'John Doe',
      phone: '+77001234567',
      delivery_type: 'delivery',
      delivery_address: 'ул. Абая 150, кв. 25',
      delivery_date: '2025-10-25',
      delivery_time: '14:00-16:00',
      payment_method: 'kaspi',
      notes: 'Пожалуйста, позвоните за 30 минут'
    };
    mockRecipientInfo = {
      name: 'Jane Smith',
      phone: '+77009876543'
    };
  });

  it('should render order information', () => {
    render(<OrderInfo />);

    expect(screen.getByText('Информация о заказе')).toBeInTheDocument();
    expect(screen.getByText('ORD-12345')).toBeInTheDocument();
    expect(screen.getByText('TRK-ABC123')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('+77001234567')).toBeInTheDocument();
  });

  it('should show delivery address for delivery type', () => {
    render(<OrderInfo />);

    expect(screen.getByText('Адрес доставки')).toBeInTheDocument();
    expect(screen.getByText('ул. Абая 150, кв. 25')).toBeInTheDocument();
  });

  it('should show pickup address for pickup type', () => {
    mockOrderData = {
      ...mockOrderData,
      delivery_type: 'pickup',
      pickup_address: 'ул. Кабанбай батыра 100',
      delivery_address: null
    };

    const { rerender } = render(<OrderInfo />);

    expect(screen.getByText('Адрес самовывоза')).toBeInTheDocument();
    expect(screen.getByText('ул. Кабанбай батыра 100')).toBeInTheDocument();
  });

  it('should display delivery date and time', () => {
    render(<OrderInfo />);

    expect(screen.getByText('Дата доставки')).toBeInTheDocument();
    expect(screen.getByText('2025-10-25')).toBeInTheDocument();
    expect(screen.getByText('Время доставки')).toBeInTheDocument();
    expect(screen.getByText('14:00-16:00')).toBeInTheDocument();
  });

  it('should display recipient information when available', () => {
    render(<OrderInfo />);

    expect(screen.getByText('Получатель')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Телефон получателя')).toBeInTheDocument();
    expect(screen.getByText('+77009876543')).toBeInTheDocument();
  });

  it('should not display recipient info when not available', () => {
    mockRecipientInfo = null;
    render(<OrderInfo />);

    expect(screen.queryByText('Получатель')).not.toBeInTheDocument();
    expect(screen.queryByText('Телефон получателя')).not.toBeInTheDocument();
  });

  it('should display order notes when available', () => {
    render(<OrderInfo />);

    expect(screen.getByText('Комментарий:')).toBeInTheDocument();
    expect(screen.getByText('Пожалуйста, позвоните за 30 минут')).toBeInTheDocument();
  });

  it('should not display notes section when notes are empty', () => {
    mockOrderData = { ...mockOrderData, notes: null };
    render(<OrderInfo />);

    expect(screen.queryByText('Комментарий:')).not.toBeInTheDocument();
  });

  it('should display payment method correctly', () => {
    render(<OrderInfo />);

    expect(screen.getByText('Способ оплаты')).toBeInTheDocument();
    expect(screen.getByText('Kaspi Pay')).toBeInTheDocument();
  });

  it('should handle cash payment method', () => {
    mockOrderData = { ...mockOrderData, payment_method: 'cash' };
    render(<OrderInfo />);

    expect(screen.getByText('Наличные')).toBeInTheDocument();
  });

  it('should copy tracking link to clipboard', async () => {
    navigator.clipboard.writeText.mockResolvedValue();

    render(<OrderInfo />);

    const copyButton = screen.getByText('Скопировать ссылку');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringContaining('/order-status/TRK-ABC123')
      );
      expect(global.alert).toHaveBeenCalledWith('Ссылка для отслеживания скопирована в буфер обмена');
    });
  });

  it('should handle clipboard copy failure', async () => {
    navigator.clipboard.writeText.mockRejectedValue(new Error('Clipboard error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<OrderInfo />);

    const copyButton = screen.getByText('Скопировать ссылку');
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('Не удалось скопировать ссылку');
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('should return null when orderData is not available', () => {
    mockOrderData = null;
    const { container } = render(<OrderInfo />);

    expect(container.firstChild).toBeNull();
  });

  it('should not display delivery time when not provided', () => {
    mockOrderData = { ...mockOrderData, delivery_time: null };
    render(<OrderInfo />);

    expect(screen.queryByText('Время доставки')).not.toBeInTheDocument();
  });
});
