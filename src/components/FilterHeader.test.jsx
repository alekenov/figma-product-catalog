import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FilterHeader from './FilterHeader';

describe('FilterHeader Component', () => {
  const defaultProps = {
    type: 'shop',
    label: 'Все товары',
    onFiltersClick: vi.fn()
  };

  const setup = (props = {}) => {
    const user = userEvent.setup();
    const utils = render(
      <FilterHeader {...defaultProps} {...props} />
    );
    return {
      user,
      ...utils,
    };
  };

  describe('Rendering', () => {
    it('should render label text', () => {
      setup({ label: 'Активные заказы' });

      expect(screen.getByText('Активные заказы')).toBeInTheDocument();
    });

    it('should render filters button', () => {
      setup();

      const filtersButton = screen.getByRole('button');
      expect(filtersButton).toBeInTheDocument();
      expect(screen.getByText('Фильтры')).toBeInTheDocument();
    });

    it('should render with proper layout classes', () => {
      const { container } = setup();

      const headerDiv = container.firstChild;
      expect(headerDiv).toHaveClass('flex', 'items-center', 'justify-between', 'px-4', 'mt-6');
    });
  });

  describe('Icon Rendering', () => {
    it('should render shop icon when type is shop', () => {
      const { container } = setup({ type: 'shop' });

      // Shop icon has specific path for bag shape
      const shopIcon = container.querySelector('svg path[d*="M17 18H3v-9.5"]');
      expect(shopIcon).toBeInTheDocument();
    });

    it('should render document icon when type is orders', () => {
      const { container } = setup({ type: 'orders' });

      // Document icon has specific path with document shape
      const documentIcon = container.querySelector('svg path[d*="M9 12h6m-6 4h6"]');
      expect(documentIcon).toBeInTheDocument();
    });

    it('should default to shop icon when type is not specified', () => {
      const { container } = render(
        <FilterHeader label="Test" onFiltersClick={vi.fn()} />
      );

      const shopIcon = container.querySelector('svg path[d*="M17 18H3v-9.5"]');
      expect(shopIcon).toBeInTheDocument();
    });

    it('should render filter icon in filters button', () => {
      const { container } = setup();

      // Filter icon has specific funnel shape
      const filterIcon = container.querySelector('svg path[d*="M4 3h12l-2 6H6L4 3z"]');
      expect(filterIcon).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should call onFiltersClick when filters button is clicked', async () => {
      const onFiltersClick = vi.fn();
      const { user } = setup({ onFiltersClick });

      const filtersButton = screen.getByRole('button');
      await user.click(filtersButton);

      expect(onFiltersClick).toHaveBeenCalledTimes(1);
    });

    it('should not prevent multiple clicks', async () => {
      const onFiltersClick = vi.fn();
      const { user } = setup({ onFiltersClick });

      const filtersButton = screen.getByRole('button');

      // Click multiple times
      await user.click(filtersButton);
      await user.click(filtersButton);
      await user.click(filtersButton);

      expect(onFiltersClick).toHaveBeenCalledTimes(3);
    });
  });

  describe('Styling', () => {
    it('should apply correct text styles', () => {
      const { container } = setup();

      const labelContainer = container.querySelector('.text-sm');
      expect(labelContainer).toBeInTheDocument();
      expect(labelContainer).toHaveClass('text-black');
    });

    it('should apply correct icon sizes', () => {
      const { container } = setup();

      const icons = container.querySelectorAll('svg');
      icons.forEach(icon => {
        expect(icon).toHaveClass('w-4', 'h-4');
      });
    });

    it('should maintain gap between icon and label', () => {
      const { container } = setup();

      const labelContainer = container.querySelector('.flex.items-center.gap-1');
      expect(labelContainer).toBeInTheDocument();
    });
  });

  describe('Props Validation', () => {
    it('should handle empty label', () => {
      setup({ label: '' });

      // Component should still render, just without visible text
      const filtersButton = screen.getByRole('button');
      expect(filtersButton).toBeInTheDocument();
    });

    it('should handle undefined onFiltersClick gracefully', async () => {
      const { user } = setup({ onFiltersClick: undefined });

      const filtersButton = screen.getByRole('button');

      // Should not throw error when clicking
      await expect(user.click(filtersButton)).resolves.not.toThrow();
    });

    it('should handle unknown type values', () => {
      const { container } = setup({ type: 'unknown' });

      // Should default to shop icon
      const shopIcon = container.querySelector('svg path[d*="M17 18H3v-9.5"]');
      expect(shopIcon).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have clickable button element', () => {
      setup();

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Фильтры');
    });

    it('should support keyboard navigation', async () => {
      const onFiltersClick = vi.fn();
      const { user } = setup({ onFiltersClick });

      // Tab to filters button
      await user.tab();
      expect(document.activeElement).toBe(screen.getByRole('button'));

      // Press Enter to activate
      await user.keyboard('{Enter}');
      expect(onFiltersClick).toHaveBeenCalledTimes(1);
    });

    it('should have proper visual hierarchy', () => {
      const { container } = setup();

      // Check that label and filter sections are visually separated
      const sections = container.firstChild.children;
      expect(sections).toHaveLength(2); // Label section and Filter button
    });
  });
});