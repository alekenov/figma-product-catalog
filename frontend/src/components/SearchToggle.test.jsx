import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchToggle from './SearchToggle';

describe('SearchToggle Component', () => {
  const defaultProps = {
    searchQuery: '',
    onSearchChange: vi.fn(),
    placeholder: 'Поиск товаров',
    enabled: true,
  };

  const setup = (props = {}) => {
    const user = userEvent.setup();
    const utils = render(
      <SearchToggle {...defaultProps} {...props} />
    );
    return {
      user,
      ...utils,
    };
  };

  describe('Initial State', () => {
    it('should render search button icon', () => {
      setup();

      const searchButton = screen.getByRole('button');
      expect(searchButton).toBeInTheDocument();
    });

    it('should show "Открыть поиск" label when not expanded', () => {
      setup();

      const searchButton = screen.getByRole('button', { name: /открыть поиск/i });
      expect(searchButton).toBeInTheDocument();
      expect(searchButton).toHaveAttribute('aria-label', 'Открыть поиск');
    });

    it('should show "Свернуть поиск" label when expanded', () => {
      setup({ isExpanded: true });

      const searchButton = screen.getByRole('button', { name: /свернуть поиск/i });
      expect(searchButton).toBeInTheDocument();
      expect(searchButton).toHaveAttribute('aria-label', 'Свернуть поиск');
    });
  });

  describe('User Interactions', () => {
    it('should toggle expanded state when clicked', async () => {
      const onExpandedChange = vi.fn();
      const { user } = setup({ onExpandedChange });

      const searchButton = screen.getByRole('button');

      // Click to expand
      await user.click(searchButton);
      expect(onExpandedChange).toHaveBeenCalledWith(true);

      // Note: In current implementation, component always renders just the button
      // The expanded state is managed but doesn't change the rendered output
    });

    it('should call onExpandedChange when toggling', async () => {
      const onExpandedChange = vi.fn();
      const { user } = setup({ onExpandedChange });

      const searchButton = screen.getByRole('button');

      // First click - expand
      await user.click(searchButton);
      expect(onExpandedChange).toHaveBeenCalledTimes(1);
      expect(onExpandedChange).toHaveBeenCalledWith(true);

      // Component would need to be re-rendered with new isExpanded prop
      // for the button to reflect the new state
    });

    it('should update aria-label based on expanded state', () => {
      // Test collapsed state
      const { rerender } = setup({ isExpanded: false });
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Открыть поиск');

      // Test expanded state
      rerender(<SearchToggle {...defaultProps} isExpanded={true} />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Свернуть поиск');
    });
  });

  describe('Disabled State', () => {
    it('should show disabled styling when enabled is false', () => {
      setup({ enabled: false });

      const searchButton = screen.getByRole('button', { name: /открыть поиск/i });
      expect(searchButton).toBeDisabled();
      expect(searchButton).toHaveClass('cursor-not-allowed', 'opacity-50');
    });

    it('should not expand when disabled', async () => {
      const { user } = setup({ enabled: false });

      const searchButton = screen.getByRole('button', { name: /открыть поиск/i });
      await user.click(searchButton);

      // Should remain collapsed
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      setup();

      const searchButton = screen.getByRole('button', { name: /открыть поиск/i });
      expect(searchButton).toHaveAttribute('aria-label', 'Открыть поиск');
    });

    it('should toggle ARIA label when state changes', () => {
      const { rerender } = setup({ isExpanded: false });

      // Initially collapsed
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Открыть поиск');

      // After expanding
      rerender(<SearchToggle {...defaultProps} isExpanded={true} />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Свернуть поиск');
    });

    it('should support keyboard navigation', async () => {
      const onExpandedChange = vi.fn();
      const { user } = setup({ onExpandedChange });

      // Tab to search button
      await user.tab();
      const searchButton = screen.getByRole('button');
      expect(searchButton).toHaveFocus();

      // Enter to toggle
      await user.keyboard('{Enter}');
      expect(onExpandedChange).toHaveBeenCalledWith(true);
    });
  });
});