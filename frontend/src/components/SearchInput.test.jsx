import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchInput from './SearchInput';

describe('SearchInput Component', () => {
  const defaultProps = {
    searchQuery: '',
    onSearchChange: vi.fn(),
    placeholder: 'Поиск товаров',
    onClose: vi.fn(),
  };

  const setup = (props = {}) => {
    const user = userEvent.setup();
    const inputRef = { current: null };
    const utils = render(
      <SearchInput {...defaultProps} {...props} inputRef={inputRef} />
    );
    return {
      user,
      inputRef,
      ...utils,
    };
  };

  describe('Rendering', () => {
    it('should render input field with placeholder', () => {
      setup();

      const searchInput = screen.getByRole('textbox');
      expect(searchInput).toBeInTheDocument();
      expect(searchInput).toHaveAttribute('placeholder', 'Поиск товаров');
    });

    it('should display search query value', () => {
      setup({ searchQuery: 'test query' });

      const searchInput = screen.getByRole('textbox');
      expect(searchInput).toHaveValue('test query');
    });

    it('should render search icon', () => {
      const { container } = setup();

      const searchIcon = container.querySelector('svg circle[cx="11"]');
      expect(searchIcon).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should call onSearchChange when typing', async () => {
      const onSearchChange = vi.fn();
      const { user } = setup({ onSearchChange });

      const searchInput = screen.getByRole('textbox');
      await user.type(searchInput, 'роза');

      // Should be called for each character
      expect(onSearchChange).toHaveBeenCalledTimes(4);
      expect(onSearchChange).toHaveBeenNthCalledWith(1, 'р');
      expect(onSearchChange).toHaveBeenNthCalledWith(2, 'о');
      expect(onSearchChange).toHaveBeenNthCalledWith(3, 'з');
      expect(onSearchChange).toHaveBeenNthCalledWith(4, 'а');
    });

    it('should show clear button when there is text', () => {
      setup({ searchQuery: 'test' });

      const clearButton = screen.getByRole('button', { name: /очистить поиск/i });
      expect(clearButton).toBeInTheDocument();
    });

    it('should not show clear button when input is empty', () => {
      setup({ searchQuery: '' });

      const clearButton = screen.queryByRole('button', { name: /очистить поиск/i });
      expect(clearButton).not.toBeInTheDocument();
    });

    it('should clear search when clear button is clicked', async () => {
      const onSearchChange = vi.fn();
      const { user } = setup({ searchQuery: 'test', onSearchChange });

      const clearButton = screen.getByRole('button', { name: /очистить поиск/i });
      await user.click(clearButton);

      expect(onSearchChange).toHaveBeenCalledWith('');
    });

    it('should call onClose on Escape when input is empty', async () => {
      const onClose = vi.fn();
      const { user } = setup({ searchQuery: '', onClose });

      const searchInput = screen.getByRole('textbox');
      await user.click(searchInput);
      await user.keyboard('{Escape}');

      expect(onClose).toHaveBeenCalled();
    });

    it('should not call onClose on Escape when input has text', async () => {
      const onClose = vi.fn();
      const { user } = setup({ searchQuery: 'test', onClose });

      const searchInput = screen.getByRole('textbox');
      await user.click(searchInput);
      await user.keyboard('{Escape}');

      expect(onClose).not.toHaveBeenCalled();
    });
  });

  describe('Focus Management', () => {
    it('should accept inputRef and allow focus control', () => {
      const { inputRef } = setup();

      expect(inputRef.current).toBeInstanceOf(HTMLInputElement);

      // Simulate external focus control
      inputRef.current.focus();
      expect(document.activeElement).toBe(inputRef.current);
    });
  });

  describe('Styling', () => {
    it('should have proper container styling', () => {
      const { container } = setup();

      const wrapper = container.querySelector('.px-4.mt-4');
      expect(wrapper).toBeInTheDocument();

      const inputContainer = container.querySelector('.relative');
      expect(inputContainer).toBeInTheDocument();
    });

    it('should apply correct input styles', () => {
      setup();

      const searchInput = screen.getByRole('textbox');
      expect(searchInput).toHaveClass('bg-gray-input-alt', 'rounded-lg', 'placeholder-gray-placeholder');
    });
  });

  describe('Accessibility', () => {
    it('should have accessible clear button', () => {
      setup({ searchQuery: 'test' });

      const clearButton = screen.getByRole('button', { name: /очистить поиск/i });
      expect(clearButton).toHaveAttribute('aria-label', 'Очистить поиск');
    });

    it('should support keyboard navigation', async () => {
      const { user } = setup({ searchQuery: 'test' });

      // Tab to input
      await user.tab();
      const searchInput = screen.getByRole('textbox');
      expect(searchInput).toHaveFocus();

      // Tab to clear button
      await user.tab();
      const clearButton = screen.getByRole('button', { name: /очистить поиск/i });
      expect(clearButton).toHaveFocus();
    });
  });
});