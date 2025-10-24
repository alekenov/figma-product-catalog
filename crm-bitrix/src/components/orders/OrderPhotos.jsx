import React from 'react';
import { useOrder } from './OrderContext';
import { useOrderPhotos } from './hooks/useOrderPhotos';

const OrderPhotos = () => {
  const { orderData, refreshOrder } = useOrder();
  const {
    isUploading,
    photoFileInputRef,
    handlePhotoClick,
    handlePhotoSelect,
    handlePhotoDelete
  } = useOrderPhotos(orderData?.id, refreshOrder);

  if (!orderData) return null;

  const hasPhotos = orderData.photos && orderData.photos.length > 0;

  return (
    <div className="bg-white rounded-lg p-4 mb-4">
      <h2 className="text-lg font-semibold mb-4">Фото заказа</h2>

      <input
        type="file"
        ref={photoFileInputRef}
        accept="image/*"
        onChange={handlePhotoSelect}
        style={{ display: 'none' }}
      />

      {hasPhotos ? (
        <div className="space-y-4">
          {orderData.photos.map((photo, index) => (
            <div key={index} className="relative">
              <img
                src={photo.url}
                alt={photo.label || 'Order photo'}
                className="w-full rounded-lg"
              />

              {photo.label && (
                <div className="mt-2 text-sm text-gray-disabled">
                  {photo.label}
                </div>
              )}

              {photo.feedback && (
                <div className="mt-2 p-3 bg-gray-50 rounded-md">
                  <div className="text-sm font-semibold text-gray-700 mb-1">
                    Отзыв клиента:
                  </div>
                  <div className="text-sm">
                    {photo.feedback === 'like' ? '👍 Понравилось' : '👎 Не понравилось'}
                  </div>
                  {photo.comment && (
                    <div className="text-sm text-gray-disabled mt-1">
                      {photo.comment}
                    </div>
                  )}
                  {photo.feedback_at && (
                    <div className="text-xs text-gray-disabled mt-1">
                      {new Date(photo.feedback_at).toLocaleString('ru-RU')}
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={handlePhotoDelete}
                className="mt-3 px-4 py-2 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors"
              >
                Удалить фото
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <svg className="w-12 h-12 mx-auto text-gray-disabled mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-disabled mb-4">Фото пока не загружено</p>
        </div>
      )}

      <button
        onClick={handlePhotoClick}
        disabled={isUploading || hasPhotos} // Disable if already has photo (only 1 photo allowed)
        className="mt-4 w-full px-4 py-2 bg-purple-primary text-white text-sm rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isUploading ? 'Загрузка...' : hasPhotos ? 'Фото уже загружено' : 'Загрузить фото'}
      </button>
    </div>
  );
};

export default OrderPhotos;
