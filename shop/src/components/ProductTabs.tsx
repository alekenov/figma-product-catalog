import { useState } from 'react';

export function ProductTabs() {
  const [activeTab, setActiveTab] = useState('description');

  const tabs = [
    { id: 'description', label: 'Описание' },
    { id: 'composition', label: 'Состав' },
    { id: 'characteristics', label: 'Характеристика' }
  ];

  return (
    <div className="mt-8 border-t border-gray-200">
      {/* Tab Headers */}
      <div className="flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-3 px-4 text-center border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-black text-black font-medium'
                : 'border-gray-300 text-gray-500'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="px-4 py-6">
        {activeTab === 'description' && (
          <div className="text-sm text-black leading-relaxed space-y-4">
            <p>
              В этом букете некоторых сезонных растений может не быть. Флорист так же аккуратно и без дополнительной стоимости подберет похожие.
            </p>
            <p>Высота: 50 см.</p>
            <p>
              Используется любой оттенок роз по умолчанию без зелени (добавьте функцию "добавить зелень")
            </p>
          </div>
        )}
        
        {activeTab === 'composition' && (
          <div className="text-sm text-black leading-relaxed">
            <p>Информация о составе букета будет добавлена позже.</p>
          </div>
        )}
        
        {activeTab === 'characteristics' && (
          <div className="text-sm text-black leading-relaxed">
            <p>Характеристики товара будут добавлены позже.</p>
          </div>
        )}
      </div>
    </div>
  );
}