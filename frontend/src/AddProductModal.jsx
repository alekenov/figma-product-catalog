import React, { useState } from 'react';

const AddProductModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    photos: [],
    video: '',
    name: '',
    price: '',
    manufacturingTime: '',
    category: '',
    flowerComposition: '',
    characteristics: '',
    description: ''
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-white z-50 flex flex-col" style={{ width: '320px', margin: '0 auto' }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#E0E0E0]">
        <button onClick={onClose} className="text-[#007AFF] text-base">
          Отмена
        </button>
        <h2 className="text-base font-semibold">Новый товар</h2>
        <button className="text-[#007AFF] text-base">
          Готово
        </button>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Product Photos Section */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Фото товара</h3>
          <div className="flex gap-2">
            {/* Add Photo Button */}
            <button className="w-20 h-20 border-2 border-dashed border-[#C7C7CC] rounded-lg flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="#C7C7CC" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
            {/* Empty photo slots */}
            {[1, 2, 3].map((index) => (
              <div key={index} className="w-20 h-20 bg-[#F2F2F7] rounded-lg"></div>
            ))}
          </div>
        </div>

        {/* Video Section */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Видео</h3>
          <button className="w-full h-32 border-2 border-dashed border-[#C7C7CC] rounded-lg flex flex-col items-center justify-center">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="#C7C7CC" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <span className="text-[#8E8E93] text-sm mt-2">Добавить видео</span>
          </button>
        </div>

        {/* Product Name */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Название товара</h3>
          <input
            type="text"
            placeholder="Введите название"
            className="w-full px-3 py-2 bg-[#F2F2F7] rounded-lg text-sm placeholder-[#8E8E93] outline-none"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
        </div>

        {/* Price */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Цена</h3>
          <div className="flex items-center bg-[#F2F2F7] rounded-lg px-3 py-2">
            <input
              type="number"
              placeholder="0"
              className="flex-1 bg-transparent text-sm placeholder-[#8E8E93] outline-none"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            />
            <span className="text-sm text-black">₸</span>
          </div>
        </div>

        {/* Manufacturing Time */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Время изготовления</h3>
          <div className="flex items-center bg-[#F2F2F7] rounded-lg px-3 py-2">
            <input
              type="number"
              placeholder="0"
              className="flex-1 bg-transparent text-sm placeholder-[#8E8E93] outline-none"
              value={formData.manufacturingTime}
              onChange={(e) => setFormData({ ...formData, manufacturingTime: e.target.value })}
            />
            <span className="text-sm text-black">дней</span>
          </div>
        </div>

        {/* Category */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Категория</h3>
            <div className="flex items-center">
              <span className="text-sm text-[#8E8E93] mr-2">Выберите</span>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 12L10 8L6 4" stroke="#C7C7CC" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Flower Composition */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Состав цветов</h3>
          <textarea
            placeholder="Опишите состав букета"
            className="w-full px-3 py-2 bg-[#F2F2F7] rounded-lg text-sm placeholder-[#8E8E93] outline-none resize-none h-20"
            value={formData.flowerComposition}
            onChange={(e) => setFormData({ ...formData, flowerComposition: e.target.value })}
          />
        </div>

        {/* Characteristics */}
        <div className="px-4 py-4 border-b border-[#E0E0E0]">
          <h3 className="text-sm font-semibold mb-3">Характеристики</h3>
          <textarea
            placeholder="Укажите размеры, вес и другие характеристики"
            className="w-full px-3 py-2 bg-[#F2F2F7] rounded-lg text-sm placeholder-[#8E8E93] outline-none resize-none h-20"
            value={formData.characteristics}
            onChange={(e) => setFormData({ ...formData, characteristics: e.target.value })}
          />
        </div>

        {/* Additional Information */}
        <div className="px-4 py-4">
          <h3 className="text-sm font-semibold mb-3">Дополнительная информация</h3>
          <textarea
            placeholder="Добавьте любую дополнительную информацию"
            className="w-full px-3 py-2 bg-[#F2F2F7] rounded-lg text-sm placeholder-[#8E8E93] outline-none resize-none h-24"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>
      </div>
    </div>
  );
};

export default AddProductModal;