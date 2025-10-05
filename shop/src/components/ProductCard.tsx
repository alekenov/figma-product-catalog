import svgPaths from "../imports/svg-rauipwsa5m";
import { useState } from 'react';

function AddButton() {
  const [isAdded, setIsAdded] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleClick = () => {
    if (isAdded) {
      // Remove from cart
      setIsAdded(false);
    } else {
      // Add to cart with animation
      setIsAnimating(true);
      setIsAdded(true);
      
      // Reset animation after completion
      setTimeout(() => {
        setIsAnimating(false);
      }, 300);
    }
  };

  return (
    <button 
      onClick={handleClick}
      className={`relative shrink-0 size-[32px] rounded-full transition-all duration-200 hover:scale-105 active:scale-95 ${
        isAnimating ? 'animate-pulse' : ''
      }`}
      aria-label={isAdded ? "Удалить из корзины" : "Добавить в корзину"}
    >
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
        <rect 
          fill={isAdded ? "var(--brand-primary)" : "var(--background-muted)"} 
          height="32" 
          rx="16" 
          width="32"
          className="transition-colors duration-200"
        />
        {isAdded ? (
          // Checkmark for added state
          <path 
            d="M10 16L14 20L22 12" 
            stroke="white" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
            className="animate-[checkmark_0.3s_ease-in-out]"
          />
        ) : (
          // Plus icon for default state
          <path 
            d="M16 9.5L16 22.5M22.5 16H9.5" 
            stroke="var(--text-primary)" 
            strokeWidth="2"
            strokeLinecap="round"
            className="transition-all duration-200"
          />
        )}
      </svg>
      

    </button>
  );
}

function DeliveryInfo() {
  return (
    <div className="flex items-center gap-1">
      <div className="w-3 h-3">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 11">
          <path clipRule="evenodd" d={svgPaths.p1a1b400} fill="var(--text-secondary)" fillRule="evenodd" />
          <path clipRule="evenodd" d={svgPaths.p26c48780} fill="var(--text-secondary)" fillRule="evenodd" />
          <path clipRule="evenodd" d={svgPaths.p3374e300} fill="var(--text-secondary)" fillRule="evenodd" />
        </svg>
      </div>
      <span className="text-caption text-[var(--text-secondary)]">Завтра к 15:30</span>
    </div>
  );
}

function Rating() {
  return null;
}


export function ProductCard({
  image,
  title,
  price,
  isFavorite = false,
  hasPreassembledBadge = false,
  onClick
}: {
  image: string;
  title: string;
  price: string;
  isFavorite?: boolean;
  hasPreassembledBadge?: boolean;
  onClick?: () => void;
}) {
  return (
    <div className="relative w-42 cursor-pointer" onClick={onClick}>
      <div className="flex flex-col gap-1 h-84">
        <div className="relative flex-1 rounded-lg overflow-hidden">
          <img
            alt={title}
            className="w-full h-full object-cover"
            src={image}
          />
          {hasPreassembledBadge && (
            <div className="absolute top-2 left-2 bg-[var(--brand-primary)] px-2 py-1 rounded-full">
              <span className="text-label text-white">Уже собрали</span>
            </div>
          )}
        </div>
        
        <div className="flex items-start justify-between">
          <div className="flex flex-col gap-1 flex-1">
            <div className="text-price text-[var(--text-primary)]">{price}</div>
            <div className="text-body text-[var(--text-primary)] leading-tight w-28 line-clamp-2">{title}</div>
          </div>
          <AddButton />
        </div>
        
        <DeliveryInfo />
        <Rating />
      </div>
    </div>
  );
}