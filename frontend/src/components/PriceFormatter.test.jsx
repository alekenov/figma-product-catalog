import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import PriceFormatter from './PriceFormatter';

/**
 * TDD Example: Writing tests FIRST for a PriceFormatter component
 * This component doesn't exist yet - this is the specification!
 *
 * RED PHASE: These tests will fail initially
 * GREEN PHASE: We'll implement the minimum code to pass
 * REFACTOR PHASE: We'll improve the code while keeping tests green
 */

describe('PriceFormatter Component - TDD Example', () => {
  describe('Basic formatting', () => {
    it('should format price with currency symbol', () => {
      render(<PriceFormatter price={1500} />);

      const formattedPrice = screen.getByText('1 500 ₸');
      expect(formattedPrice).toBeInTheDocument();
    });

    it('should handle zero price', () => {
      render(<PriceFormatter price={0} />);

      const formattedPrice = screen.getByText('0 ₸');
      expect(formattedPrice).toBeInTheDocument();
    });

    it('should format large numbers with spaces', () => {
      render(<PriceFormatter price={1234567} />);

      const formattedPrice = screen.getByText('1 234 567 ₸');
      expect(formattedPrice).toBeInTheDocument();
    });
  });

  describe('Display variants', () => {
    it('should support inline display variant', () => {
      const { container } = render(
        <PriceFormatter price={1500} variant="inline" />
      );

      const element = container.querySelector('span');
      expect(element).toBeInTheDocument();
      expect(element).toHaveTextContent('1 500 ₸');
    });

    it('should support large display variant with special styling', () => {
      const { container } = render(
        <PriceFormatter price={1500} variant="large" />
      );

      const element = container.querySelector('.text-2xl');
      expect(element).toBeInTheDocument();
      expect(element).toHaveClass('font-bold');
    });

    it('should support small display variant', () => {
      const { container } = render(
        <PriceFormatter price={1500} variant="small" />
      );

      const element = container.querySelector('.text-sm');
      expect(element).toBeInTheDocument();
    });
  });

  describe('Color schemes', () => {
    it('should support success color for positive values', () => {
      const { container } = render(
        <PriceFormatter price={1500} color="success" />
      );

      const element = container.querySelector('.text-green-success');
      expect(element).toBeInTheDocument();
    });

    it('should support error color for negative values', () => {
      const { container } = render(
        <PriceFormatter price={-500} color="error" />
      );

      const element = container.querySelector('.text-red-500');
      expect(element).toBeInTheDocument();
      expect(element).toHaveTextContent('-500 ₸');
    });

    it('should use default color when not specified', () => {
      const { container } = render(<PriceFormatter price={1500} />);

      const element = container.querySelector('.text-gray-900');
      expect(element).toBeInTheDocument();
    });
  });

  describe('Additional features', () => {
    it('should show plus sign for positive changes', () => {
      render(<PriceFormatter price={1500} showSign={true} />);

      const formattedPrice = screen.getByText('+1 500 ₸');
      expect(formattedPrice).toBeInTheDocument();
    });

    it('should not show plus sign by default', () => {
      render(<PriceFormatter price={1500} />);

      const formattedPrice = screen.getByText('1 500 ₸');
      expect(formattedPrice).toBeInTheDocument();
    });

    it('should support custom currency', () => {
      render(<PriceFormatter price={1500} currency="$" />);

      const formattedPrice = screen.getByText('$1 500');
      expect(formattedPrice).toBeInTheDocument();
    });

    it('should handle undefined price gracefully', () => {
      render(<PriceFormatter price={undefined} />);

      const formattedPrice = screen.getByText('—');
      expect(formattedPrice).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA label for screen readers', () => {
      const { container } = render(<PriceFormatter price={1500} />);

      const element = container.firstChild;
      expect(element).toHaveAttribute('aria-label', '1500 тенге');
    });

    it('should indicate negative values in ARIA label', () => {
      const { container } = render(<PriceFormatter price={-500} />);

      const element = container.firstChild;
      expect(element).toHaveAttribute('aria-label', 'минус 500 тенге');
    });
  });
});