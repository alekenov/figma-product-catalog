import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

// Mock hooks and context - MUST be before imports
const mockRefreshOrder = vi.fn();
const mockHandlePhotoClick = vi.fn();
const mockHandlePhotoSelect = vi.fn();
const mockHandlePhotoDelete = vi.fn();
const mockPhotoFileInputRef = { current: null };

let mockOrderData = {
  id: 123,
  photos: [
    {
      url: 'https://example.com/photo1.jpg',
      label: 'Букет готов к доставке',
      feedback: 'like',
      comment: 'Очень красиво!',
      feedback_at: '2025-10-23T14:30:00'
    }
  ]
};

let mockIsUploading = false;

vi.mock('./OrderContext', () => ({
  useOrder: () => ({
    orderData: mockOrderData,
    refreshOrder: mockRefreshOrder
  })
}));

vi.mock('./hooks/useOrderPhotos', () => ({
  useOrderPhotos: () => ({
    isUploading: mockIsUploading,
    photoFileInputRef: mockPhotoFileInputRef,
    handlePhotoClick: mockHandlePhotoClick,
    handlePhotoSelect: mockHandlePhotoSelect,
    handlePhotoDelete: mockHandlePhotoDelete
  })
}));

import OrderPhotos from './OrderPhotos';

describe('OrderPhotos', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset to default state
    mockOrderData = {
      id: 123,
      photos: [
        {
          url: 'https://example.com/photo1.jpg',
          label: 'Букет готов к доставке',
          feedback: 'like',
          comment: 'Очень красиво!',
          feedback_at: '2025-10-23T14:30:00'
        }
      ]
    };
    mockIsUploading = false;
  });

  it('should render photos section header', () => {
    render(<OrderPhotos />);

    expect(screen.getByText('Фото заказа')).toBeInTheDocument();
  });

  it('should display photo when available', () => {
    render(<OrderPhotos />);

    const image = screen.getByAltText('Букет готов к доставке');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'https://example.com/photo1.jpg');
  });

  it('should display photo label', () => {
    render(<OrderPhotos />);

    expect(screen.getByText('Букет готов к доставке')).toBeInTheDocument();
  });

  it('should display customer feedback with like', () => {
    render(<OrderPhotos />);

    expect(screen.getByText('Отзыв клиента:')).toBeInTheDocument();
    expect(screen.getByText('👍 Понравилось')).toBeInTheDocument();
  });

  it('should display feedback comment', () => {
    render(<OrderPhotos />);

    expect(screen.getByText('Очень красиво!')).toBeInTheDocument();
  });

  it('should display delete button', () => {
    render(<OrderPhotos />);

    expect(screen.getByText('Удалить фото')).toBeInTheDocument();
  });

  it('should call delete handler when delete button is clicked', () => {
    render(<OrderPhotos />);

    const deleteButton = screen.getByText('Удалить фото');
    fireEvent.click(deleteButton);

    expect(mockHandlePhotoDelete).toHaveBeenCalled();
  });

  it('should display empty state when no photos', () => {
    mockOrderData = {
      id: 123,
      photos: []
    };

    render(<OrderPhotos />);

    expect(screen.getByText('Фото пока не загружено')).toBeInTheDocument();
  });

  it('should show upload button enabled when no photos', () => {
    mockOrderData = {
      id: 123,
      photos: []
    };

    render(<OrderPhotos />);

    const uploadButton = screen.getByText('Загрузить фото');
    expect(uploadButton).toBeInTheDocument();
    expect(uploadButton).not.toBeDisabled();
  });

  it('should show upload button disabled when photo already exists', () => {
    render(<OrderPhotos />);

    const uploadButton = screen.getByText('Фото уже загружено');
    expect(uploadButton).toBeInTheDocument();
    expect(uploadButton).toBeDisabled();
  });

  it('should trigger file input when upload button is clicked', () => {
    mockOrderData = {
      id: 123,
      photos: []
    };

    render(<OrderPhotos />);

    const uploadButton = screen.getByText('Загрузить фото');
    fireEvent.click(uploadButton);

    expect(mockHandlePhotoClick).toHaveBeenCalled();
  });

  it('should have hidden file input with correct attributes', () => {
    const { container } = render(<OrderPhotos />);

    const fileInput = container.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('accept', 'image/*');
    expect(fileInput).toHaveStyle({ display: 'none' });
  });

  it('should return null when orderData is not available', () => {
    mockOrderData = null;

    const { container } = render(<OrderPhotos />);

    expect(container.firstChild).toBeNull();
  });
});
