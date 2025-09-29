import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BottomNavBar from './BottomNavBar';

describe('BottomNavBar Component', () => {
  const defaultProps = {
    activeTab: 'products',
    onTabChange: vi.fn()
  };

  const setup = (props = {}) => {
    const user = userEvent.setup();
    const utils = render(
      <BottomNavBar {...defaultProps} {...props} />
    );
    return {
      user,
      ...utils,
    };
  };

  describe('Rendering', () => {
    it('should render all navigation items', () => {
      setup();

      // Check all 5 navigation items are present
      expect(screen.getByText('Заказы')).toBeInTheDocument();
      expect(screen.getByText('Товары')).toBeInTheDocument();
      expect(screen.getByText('Склад')).toBeInTheDocument();
      expect(screen.getByText('Клиенты')).toBeInTheDocument();
      expect(screen.getByText('Профиль')).toBeInTheDocument();
    });

    it('should render with fixed positioning at bottom', () => {
      const { container } = setup();

      const navBar = container.firstChild;
      expect(navBar).toHaveClass('fixed', 'bottom-0');
    });

    it('should have mobile width constraint', () => {
      const { container } = setup();

      const navBar = container.firstChild;
      expect(navBar).toHaveClass('w-[320px]');
    });
  });

  describe('Active State', () => {
    it('should highlight active tab with purple color', () => {
      setup({ activeTab: 'orders' });

      const ordersTab = screen.getByText('Заказы');
      expect(ordersTab).toHaveClass('text-purple-primary');
    });

    it('should show inactive tabs in gray', () => {
      setup({ activeTab: 'orders' });

      const productsTab = screen.getByText('Товары');
      expect(productsTab).toHaveClass('text-gray-disabled');
    });

    it('should update active state when prop changes', () => {
      const { rerender } = setup({ activeTab: 'products' });

      // Initially products is active
      expect(screen.getByText('Товары')).toHaveClass('text-purple-primary');

      // Change active tab to warehouse
      rerender(<BottomNavBar {...defaultProps} activeTab="warehouse" />);
      expect(screen.getByText('Склад')).toHaveClass('text-purple-primary');
      expect(screen.getByText('Товары')).toHaveClass('text-gray-disabled');
    });
  });

  describe('User Interactions', () => {
    it('should call onTabChange when clicking orders tab', async () => {
      const onTabChange = vi.fn();
      const { user } = setup({ onTabChange });

      const ordersButton = screen.getByText('Заказы').closest('button');
      await user.click(ordersButton);

      expect(onTabChange).toHaveBeenCalledWith('orders', '/orders');
    });

    it('should call onTabChange when clicking products tab', async () => {
      const onTabChange = vi.fn();
      const { user } = setup({ onTabChange });

      const productsButton = screen.getByText('Товары').closest('button');
      await user.click(productsButton);

      expect(onTabChange).toHaveBeenCalledWith('products', '/');
    });

    it('should call onTabChange when clicking warehouse tab', async () => {
      const onTabChange = vi.fn();
      const { user } = setup({ onTabChange });

      const warehouseButton = screen.getByText('Склад').closest('button');
      await user.click(warehouseButton);

      expect(onTabChange).toHaveBeenCalledWith('warehouse', '/warehouse');
    });

    it('should call onTabChange when clicking clients tab', async () => {
      const onTabChange = vi.fn();
      const { user } = setup({ onTabChange });

      const clientsButton = screen.getByText('Клиенты').closest('button');
      await user.click(clientsButton);

      expect(onTabChange).toHaveBeenCalledWith('clients', '/clients');
    });

    it('should call onTabChange when clicking profile tab', async () => {
      const onTabChange = vi.fn();
      const { user } = setup({ onTabChange });

      const profileButton = screen.getByText('Профиль').closest('button');
      await user.click(profileButton);

      expect(onTabChange).toHaveBeenCalledWith('profile', '/profile');
    });
  });

  describe('Icons', () => {
    it('should render SVG icons for each tab', () => {
      const { container } = setup();

      // Check that SVG elements exist for each nav item
      const buttons = container.querySelectorAll('button');
      expect(buttons).toHaveLength(5);

      buttons.forEach((button) => {
        const svg = button.querySelector('svg');
        expect(svg).toBeInTheDocument();
      });
    });

    it('should apply active color to icon when tab is active', () => {
      const { container } = setup({ activeTab: 'warehouse' });

      // Find warehouse button by text, then check its icon
      const warehouseButton = screen.getByText('Склад').closest('button');
      const warehouseIcon = warehouseButton.querySelector('svg');

      // Icon should have active color class
      expect(warehouseIcon).toHaveClass('stroke-purple-primary');
    });

    it('should apply disabled color to icon when tab is inactive', () => {
      const { container } = setup({ activeTab: 'warehouse' });

      // Find orders button (inactive) and check its icon
      const ordersButton = screen.getByText('Заказы').closest('button');
      const ordersIcon = ordersButton.querySelector('svg');

      expect(ordersIcon).toHaveClass('stroke-gray-disabled');
    });
  });

  describe('Layout', () => {
    it('should use flexbox for equal spacing', () => {
      const { container } = setup();

      const flexContainer = container.querySelector('.flex.h-full');
      expect(flexContainer).toBeInTheDocument();

      // Each button should have flex-1 class
      const buttons = container.querySelectorAll('button');
      buttons.forEach((button) => {
        expect(button).toHaveClass('flex-1');
      });
    });

    it('should stack icon and label vertically', () => {
      const { container } = setup();

      const buttons = container.querySelectorAll('button');
      buttons.forEach((button) => {
        expect(button).toHaveClass('flex-col');
      });
    });
  });

  describe('Accessibility', () => {
    it('should have clickable button elements', () => {
      setup();

      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(5);
    });

    it('should support keyboard navigation', async () => {
      const onTabChange = vi.fn();
      const { user } = setup({ onTabChange });

      // Tab through navigation items
      await user.tab();
      expect(document.activeElement).toBe(screen.getAllByRole('button')[0]);

      // Press Enter to select
      await user.keyboard('{Enter}');
      expect(onTabChange).toHaveBeenCalledTimes(1);
    });
  });
});