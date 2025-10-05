import React from 'react';
import StoreCard from './StoreCard';
import SectionHeader from './SectionHeader';

/**
 * PopularStores - секция "Популярные магазины"
 *
 * Дизайн из Figma: Секция с заголовком и вертикальным списком карточек магазинов
 *
 * @param {Array} stores - Массив магазинов для отображения
 * @param {function} onShowAll - Колбэк при клике "Все магазины"
 * @param {function} onStoreClick - Колбэк при клике на карточку магазина
 */
export default function PopularStores({
  stores = [],
  onShowAll,
  onStoreClick
}) {
  return (
    <div className="flex flex-col gap-[16px] w-full">
      {/* Section Header */}
      <SectionHeader
        title="Популярные магазины"
        linkText="Все магазины"
        onShowAll={onShowAll}
      />

      {/* Store Cards - вертикальный список */}
      <div className="flex flex-col gap-[12px] w-full">
        {stores.map(store => (
          <StoreCard
            key={store.id}
            image={store.image}
            badgeText={store.badgeText}
            badgeColor={store.badgeColor}
            name={store.name}
            rating={store.rating}
            reviewsCount={store.reviewsCount}
            status={store.status}
            statusText={store.statusText}
            deliveryTime={store.deliveryTime}
            deliveryPrice={store.deliveryPrice}
            onClick={() => onStoreClick?.(store.id)}
          />
        ))}
      </div>

      {/* Empty State */}
      {stores.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>Нет доступных магазинов</p>
        </div>
      )}
    </div>
  );
}
