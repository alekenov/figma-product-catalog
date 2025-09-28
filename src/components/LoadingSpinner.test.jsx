import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from './LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('should render loading text', () => {
    render(<LoadingSpinner />);

    const loadingText = screen.getByText('Загрузка...');
    expect(loadingText).toBeInTheDocument();
  });

  it('should have spinner animation class', () => {
    const { container } = render(<LoadingSpinner />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('border-purple-primary');
  });

  it('should use figma container for mobile layout', () => {
    const { container } = render(<LoadingSpinner />);

    const figmaContainer = container.querySelector('.figma-container');
    expect(figmaContainer).toBeInTheDocument();
    expect(figmaContainer).toHaveClass('flex', 'items-center', 'justify-center');
  });
});