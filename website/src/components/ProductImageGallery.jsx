import React, { useState } from 'react';

/**
 * ProductImageGallery - галерея изображений товара
 * Поддерживает множественные изображения с переключением
 *
 * @param {Array<string>} images - Массив URL изображений
 * @param {string} alt - Альтернативный текст
 */
export default function ProductImageGallery({ images = [], alt }) {
  const [activeIndex, setActiveIndex] = useState(0);

  // Если передан один URL как строка, преобразуем в массив
  const imageArray = Array.isArray(images) ? images : [images];
  const currentImage = imageArray[activeIndex] || imageArray[0];

  return (
    <div className="space-y-3">
      {/* Main Image */}
      <div className="w-full aspect-square rounded-lg overflow-hidden bg-bg-light">
        <img
          src={currentImage}
          alt={alt}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Thumbnails (если больше одного изображения) */}
      {imageArray.length > 1 && (
        <div className="flex gap-2 overflow-x-auto">
          {imageArray.map((image, index) => (
            <button
              key={index}
              onClick={() => setActiveIndex(index)}
              className={`flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border-2 transition-colors ${
                index === activeIndex
                  ? 'border-pink'
                  : 'border-bg-light hover:border-bg-extra-light'
              }`}
            >
              <img
                src={image}
                alt={`${alt} ${index + 1}`}
                className="w-full h-full object-cover"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}