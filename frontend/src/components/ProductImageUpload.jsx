import React, { useState, useRef } from 'react';
import { useToast } from './ToastProvider';

/**
 * ProductImageUpload - Component for uploading product images to R2
 *
 * @param {Array} images - Array of image URLs
 * @param {Function} onImagesChange - Callback when images change
 * @param {number} maxImages - Maximum number of images (default: 10)
 */
const ProductImageUpload = ({ images = [], onImagesChange, maxImages = 10 }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);
  const { showSuccess, showError } = useToast();

  const IMAGE_WORKER_URL = 'https://flower-shop-images.alekenov.workers.dev';

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Check if we'll exceed max images
    if (images.length + files.length > maxImages) {
      showError?.(`Максимум ${maxImages} фото`);
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const uploadedUrls = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Validate file type
        if (!file.type.startsWith('image/')) {
          showError?.(`${file.name} не является изображением`);
          continue;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          showError?.(`${file.name} превышает 10MB`);
          continue;
        }

        // Upload to R2
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${IMAGE_WORKER_URL}/upload`, {
          method: 'POST',
          body: formData,
        });

        setUploadProgress(Math.round(((i + 1) / files.length) * 100));

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.error || 'Upload failed');
        }

        const result = await response.json();
        uploadedUrls.push(result.url);
      }

      // Update parent component with new images
      const newImages = [...images, ...uploadedUrls];
      onImagesChange?.(newImages);

      showSuccess?.(`${uploadedUrls.length} фото загружено`);
    } catch (error) {
      console.error('Error uploading photos:', error);
      showError?.(`Ошибка загрузки: ${error.message}`);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemoveImage = (indexToRemove) => {
    const newImages = images.filter((_, index) => index !== indexToRemove);
    onImagesChange?.(newImages);
    showSuccess?.('Фото удалено');
  };

  const handleAddPhotos = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="px-4 py-4">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        className="hidden"
      />

      {images.length === 0 ? (
        /* Empty State */
        <div
          onClick={handleAddPhotos}
          className="bg-gray-input-alt rounded p-6 text-center cursor-pointer hover:bg-gray-neutral/30 transition-colors"
        >
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" className="mx-auto mb-3">
            <rect x="3" y="8" width="22" height="16" rx="2" stroke="black" strokeWidth="1.5"/>
            <circle cx="14" cy="16" r="4" stroke="black" strokeWidth="1.5"/>
            <path d="M10 8V6C10 5.44772 10.4477 5 11 5H17C17.5523 5 18 5.44772 18 6V8" stroke="black" strokeWidth="1.5"/>
          </svg>
          <p className="text-[15px] font-['Open_Sans'] mb-2">
            {isUploading ? `Загрузка... ${uploadProgress}%` : 'Добавьте фотографии товара'}
          </p>
          <p className="text-[13px] text-gray-disabled font-['Open_Sans']">
            Не более {maxImages} фото, jpg, jpeg, png.
          </p>
        </div>
      ) : (
        /* Uploaded Images Grid */
        <div>
          <div className="grid grid-cols-3 gap-2 mb-3">
            {images.map((imageUrl, index) => (
              <div key={index} className="relative aspect-square bg-gray-input rounded-lg overflow-hidden group">
                <img
                  src={imageUrl}
                  alt={`Product ${index + 1}`}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
                <button
                  onClick={() => handleRemoveImage(index)}
                  className="absolute top-1 right-1 w-6 h-6 bg-black/60 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  aria-label="Удалить фото"
                >
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M9 3L3 9M3 3L9 9" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                  </svg>
                </button>
                {index === 0 && (
                  <div className="absolute bottom-1 left-1 px-2 py-0.5 bg-purple-primary text-white text-xs rounded">
                    Главное
                  </div>
                )}
              </div>
            ))}
          </div>

          {images.length < maxImages && (
            <button
              onClick={handleAddPhotos}
              disabled={isUploading}
              className="w-full py-3 border-2 border-dashed border-gray-border rounded text-sm font-['Open_Sans'] text-purple-primary hover:bg-purple-50 transition-colors disabled:opacity-50"
            >
              {isUploading ? `Загрузка... ${uploadProgress}%` : '+ Добавить ещё фото'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ProductImageUpload;