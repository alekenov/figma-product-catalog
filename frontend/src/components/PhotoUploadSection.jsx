import React, { useState, useRef } from 'react';
import { useToast } from './ToastProvider';

const PhotoUploadSection = ({ orderId, onPhotoUpload }) => {
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);
  const { showSuccess } = useToast();

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('Размер файла не должен превышать 10MB');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Upload to Cloudflare Worker
      const formData = new FormData();
      formData.append('file', file);

      setUploadProgress(30);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      setUploadProgress(70);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Upload failed');
      }

      const result = await response.json();
      setUploadProgress(100);

      const photoData = {
        id: result.imageId,
        name: file.name,
        size: result.size,
        type: result.type,
        url: result.url,
        uploadedAt: new Date().toISOString()
      };

      setUploadedPhoto(photoData);

      // Store reference in localStorage (just URL, not base64)
      localStorage.setItem(`order_photo_${orderId}`, JSON.stringify(photoData));

      // Show success notification
      showSuccess('Фото добавлено, заказ собран');

      // Notify parent component
      if (onPhotoUpload) {
        onPhotoUpload(photoData);
      }
    } catch (error) {
      console.error('Error uploading photo:', error);
      alert(`Ошибка при загрузке фото: ${error.message}`);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleRemovePhoto = () => {
    setUploadedPhoto(null);
    localStorage.removeItem(`order_photo_${orderId}`);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    showSuccess('Фото удалено');
  };

  const handleChangePhoto = () => {
    fileInputRef.current?.click();
  };

  const handleAddPhoto = () => {
    fileInputRef.current?.click();
  };

  // Load photo from localStorage on component mount
  React.useEffect(() => {
    const savedPhoto = localStorage.getItem(`order_photo_${orderId}`);
    if (savedPhoto) {
      try {
        setUploadedPhoto(JSON.parse(savedPhoto));
      } catch (error) {
        console.error('Error loading saved photo:', error);
      }
    }
  }, [orderId]);

  return (
    <div className="mt-4">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      {!uploadedPhoto ? (
        /* Empty State - "Не добавлено" */
        <div className="border-2 border-dashed border-gray-border rounded-lg p-6 text-center">
          <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-3">
            Не добавлено
          </div>
          <div className="w-12 h-12 mx-auto mb-3 bg-gray-input rounded-full flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 16.5V18.75C3 19.993 4.007 21 5.25 21H18.75C19.993 21 21 19.993 21 18.75V16.5M16.5 12L12 16.5M12 16.5L7.5 12M12 16.5V3"
                stroke="#828282"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <button
            onClick={handleAddPhoto}
            disabled={isUploading}
            className="text-sm font-['Open_Sans'] text-purple-primary hover:text-purple-600 transition-colors disabled:opacity-50"
          >
            {isUploading ? `Загрузка... ${uploadProgress}%` : 'добавить фото'}
          </button>
        </div>
      ) : (
        /* Uploaded State - "Добавлено" */
        <div className="border border-gray-border rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="w-16 h-16 bg-gray-input rounded-lg overflow-hidden flex-shrink-0">
              <img
                src={uploadedPhoto.url}
                alt="Uploaded photo"
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">
                Добавлено
              </div>
              <div className="text-sm font-['Open_Sans'] text-black mb-2 truncate">
                {uploadedPhoto.name}
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleChangePhoto}
                  className="text-xs font-['Open_Sans'] text-purple-primary hover:text-purple-600 transition-colors"
                >
                  Изменить
                </button>
                <button
                  onClick={handleRemovePhoto}
                  className="text-xs font-['Open_Sans'] text-error-primary hover:text-red-600 transition-colors"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhotoUploadSection;