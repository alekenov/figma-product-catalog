import { useState, useRef } from 'react';
import { ordersAPI } from '../../../services';

export const useOrderPhotos = (orderId, onSuccess) => {
  const [isUploading, setIsUploading] = useState(false);
  const photoFileInputRef = useRef(null);

  const handlePhotoClick = () => {
    photoFileInputRef.current?.click();
  };

  const handlePhotoSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('Размер файла не должен превышать 10 МБ');
      return;
    }

    try {
      setIsUploading(true);
      await ordersAPI.uploadOrderPhoto(orderId, file);

      // Clear input
      event.target.value = '';

      // Call success callback to refresh order data
      if (onSuccess) await onSuccess();

    } catch (err) {
      console.error('Error uploading photo:', err);
      alert(`Ошибка загрузки: ${err.message}`);

      // Clear input even on error
      event.target.value = '';
    } finally {
      setIsUploading(false);
    }
  };

  const handlePhotoDelete = async () => {
    if (!confirm('Удалить фото?')) return;

    try {
      await ordersAPI.deleteOrderPhoto(orderId);

      // Call success callback to refresh order data
      if (onSuccess) await onSuccess();

    } catch (err) {
      console.error('Error deleting photo:', err);
      alert(`Ошибка удаления: ${err.message}`);
    }
  };

  return {
    isUploading,
    photoFileInputRef,
    handlePhotoClick,
    handlePhotoSelect,
    handlePhotoDelete
  };
};
