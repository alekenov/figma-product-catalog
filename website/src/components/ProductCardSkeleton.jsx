import React from 'react';

/**
 * ProductCardSkeleton - скелетон для ProductCard во время загрузки
 *
 * Использует дизайн-систему Cvety.kz:
 * - Цвета: bg-bg-light, bg-bg-secondary
 * - Spacing: gap-3, p-3
 * - Border radius: rounded-lg
 * - Анимация: animate-pulse
 */
export default function ProductCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 animate-pulse">
      {/* Image skeleton */}
      <div className="relative w-full aspect-square bg-bg-light rounded-lg overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-bg-light via-bg-secondary to-bg-light animate-shimmer" />
      </div>

      {/* Content skeleton */}
      <div className="flex flex-col gap-2">
        {/* Price skeleton */}
        <div className="flex items-center justify-between">
          <div className="h-6 w-20 bg-bg-light rounded" />
          <div className="h-8 w-8 bg-bg-light rounded-full" />
        </div>

        {/* Title skeleton */}
        <div className="h-4 w-3/4 bg-bg-light rounded" />

        {/* Delivery info skeleton */}
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 bg-bg-light rounded" />
          <div className="h-3 w-24 bg-bg-light rounded" />
        </div>
      </div>
    </div>
  );
}