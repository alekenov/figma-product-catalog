import { useState } from 'react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface ProductImage {
  id: string;
  url: string;
  alt: string;
}

export function ProductImageCarousel() {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const images: ProductImage[] = [
    {
      id: '1',
      url: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=400&h=500&fit=crop',
      alt: 'Букет розовых пионов - основное фото'
    },
    {
      id: '2', 
      url: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=500&fit=crop',
      alt: 'Букет розовых пионов - вид сбоку'
    },
    {
      id: '3',
      url: 'https://images.unsplash.com/photo-1586323679421-bd85e3ac25b1?w=400&h=500&fit=crop', 
      alt: 'Букет розовых пионов - детали'
    }
  ];

  const goToImage = (index: number) => {
    setCurrentImageIndex(index);
  };

  const goToPrevious = () => {
    setCurrentImageIndex(prev => prev === 0 ? images.length - 1 : prev - 1);
  };

  const goToNext = () => {
    setCurrentImageIndex(prev => prev === images.length - 1 ? 0 : prev + 1);
  };

  return (
    <div className="relative w-full">
      {/* Main Image */}
      <div className="relative aspect-[4/5] bg-white rounded-[var(--radius-md)] overflow-hidden">
        <ImageWithFallback
          src={images[currentImageIndex].url}
          alt={images[currentImageIndex].alt}
          className="w-full h-full object-cover"
        />
        
        {/* Navigation Arrows */}
        {images.length > 1 && (
          <>
            <button
              onClick={goToPrevious}
              className="absolute left-4 top-1/2 -translate-y-1/2 w-8 h-8 bg-white/80 rounded-full flex items-center justify-center hover:bg-white transition-colors"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M10 4L6 8L10 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            
            <button
              onClick={goToNext}
              className="absolute right-4 top-1/2 -translate-y-1/2 w-8 h-8 bg-white/80 rounded-full flex items-center justify-center hover:bg-white transition-colors"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M6 4L10 8L6 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </>
        )}
        
        {/* Page Indicator */}
        {images.length > 1 && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
            {images.map((_, index) => (
              <button
                key={index}
                onClick={() => goToImage(index)}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index === currentImageIndex 
                    ? 'bg-[var(--brand-primary)]' 
                    : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* Thumbnail Strip */}
      {images.length > 1 && (
        <div className="flex gap-2 mt-3 px-[var(--spacing-4)]">
          {images.map((image, index) => (
            <button
              key={image.id}
              onClick={() => goToImage(index)}
              className={`relative flex-shrink-0 w-16 h-16 rounded-[var(--radius-sm)] overflow-hidden border-2 transition-colors ${
                index === currentImageIndex 
                  ? 'border-[var(--brand-primary)]' 
                  : 'border-transparent'
              }`}
            >
              <ImageWithFallback
                src={image.url}
                alt={image.alt}
                className="w-full h-full object-cover"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}