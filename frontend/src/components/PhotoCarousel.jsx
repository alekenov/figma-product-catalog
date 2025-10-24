import React, { useState, useRef } from 'react';

/**
 * PhotoCarousel component
 * Displays a carousel/gallery of product images with navigation
 *
 * @param {string[]} images - Array of image URLs
 * @param {string} alt - Alt text for images
 */
const PhotoCarousel = ({ images, alt = '' }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollContainerRef = useRef(null);

  // If no images, show placeholder
  if (!images || images.length === 0) {
    return (
      <div className="w-full h-[300px] bg-gray-input flex items-center justify-center rounded">
        <span className="text-gray-placeholder font-['Open_Sans']">Нет фото</span>
      </div>
    );
  }

  // If only one image, show it without navigation
  if (images.length === 1) {
    return (
      <div className="w-full h-[300px] rounded overflow-hidden">
        <img
          src={images[0]}
          alt={alt}
          className="w-full h-full object-cover"
        />
      </div>
    );
  }

  const handlePrev = () => {
    const newIndex = currentIndex === 0 ? images.length - 1 : currentIndex - 1;
    setCurrentIndex(newIndex);
    scrollToIndex(newIndex);
  };

  const handleNext = () => {
    const newIndex = currentIndex === images.length - 1 ? 0 : currentIndex + 1;
    setCurrentIndex(newIndex);
    scrollToIndex(newIndex);
  };

  const scrollToIndex = (index) => {
    if (scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      const scrollLeft = index * container.offsetWidth;
      container.scrollTo({ left: scrollLeft, behavior: 'smooth' });
    }
  };

  const handleDotClick = (index) => {
    setCurrentIndex(index);
    scrollToIndex(index);
  };

  return (
    <div className="relative w-full h-[300px] rounded overflow-hidden">
      {/* Images container with scroll snap */}
      <div
        ref={scrollContainerRef}
        className="flex overflow-x-auto snap-x snap-mandatory scrollbar-hide h-full"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {images.map((image, index) => (
          <div
            key={index}
            className="flex-shrink-0 w-full h-full snap-center"
          >
            <img
              src={image}
              alt={`${alt} - фото ${index + 1}`}
              className="w-full h-full object-cover"
            />
          </div>
        ))}
      </div>

      {/* Previous button */}
      <button
        onClick={handlePrev}
        className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-white bg-opacity-80 rounded-full flex items-center justify-center hover:bg-opacity-100 transition-all shadow-md"
        aria-label="Предыдущее фото"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Next button */}
      <button
        onClick={handleNext}
        className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-white bg-opacity-80 rounded-full flex items-center justify-center hover:bg-opacity-100 transition-all shadow-md"
        aria-label="Следующее фото"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Dots indicator */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2">
        {images.map((_, index) => (
          <button
            key={index}
            onClick={() => handleDotClick(index)}
            className={`
              w-2 h-2 rounded-full transition-all
              ${index === currentIndex ? 'bg-white w-6' : 'bg-white bg-opacity-50'}
            `}
            aria-label={`Перейти к фото ${index + 1}`}
          />
        ))}
      </div>

      {/* Photo counter */}
      <div className="absolute top-3 right-3 bg-black bg-opacity-60 text-white px-2 py-1 rounded text-xs font-['Open_Sans']">
        {currentIndex + 1} / {images.length}
      </div>
    </div>
  );
};

export default PhotoCarousel;
