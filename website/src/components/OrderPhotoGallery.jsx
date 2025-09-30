import React from 'react';

/**
 * OrderPhotoGallery - галерея фотографий заказа
 *
 * @param {Array} photos - Массив объектов с фото [{url, label}]
 * @param {string} noticeText - Текст уведомления под галереей
 */
export default function OrderPhotoGallery({
  photos = [],
  noticeText = 'Мы отправим sms получателю для самостоятельной загрузки фотоотзыва.'
}) {
  return (
    <div className="space-y-4">
      {/* Photo Grid */}
      <div className="grid grid-cols-2 gap-4">
        {photos.map((photo, index) => (
          <div key={index} className="space-y-2">
            <img
              src={photo.url}
              alt={photo.label}
              className="w-full h-[250px] object-cover rounded-lg"
            />
            <p className="font-sans font-normal text-[14px] leading-[1.3] text-text-black">
              {photo.label}
            </p>
          </div>
        ))}
      </div>

      {/* Notice Text */}
      {noticeText && (
        <p className="font-sans font-normal text-[14px] leading-[1.3] text-text-grey-dark">
          {noticeText}
        </p>
      )}
    </div>
  );
}