import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsAPI } from './services/api';
import ProductImageUpload from './components/ProductImageUpload';
import './App.css';

const AddProduct = () => {
  const navigate = useNavigate();

  // Предустановленные цвета для тегов
  const availableColors = [
    { id: 'red', name: 'Красный', color: '#FF4444' },
    { id: 'pink', name: 'Розовый', color: '#FFB6C1' },
    { id: 'white', name: 'Белый', color: '#FFFFFF', border: true },
    { id: 'yellow', name: 'Желтый', color: '#FFD700' },
    { id: 'purple', name: 'Фиолетовый', color: '#9370DB' },
    { id: 'orange', name: 'Оранжевый', color: '#FFA500' },
    { id: 'mixed', name: 'Микс', color: 'linear-gradient(90deg, #FF4444, #FFB6C1, #FFD700)' }
  ];

  // Предустановленные цветы (в будущем будут загружаться из API склада)
  const availableFlowers = [
    'Роза',
    'Тюльпан',
    'Пион',
    'Хризантема',
    'Лилия',
    'Гвоздика',
    'Альстромерия',
    'Эустома',
    'Гипсофила',
    'Ромашка'
  ];

  const [formData, setFormData] = useState({
    photos: [],
    name: '',
    price: '',
    manufacturingTime: '',
    category: 'Сборный букет/Букеты',
    flowers: [],
    selectedColors: [],
    width: '',
    height: '',
    shelfLife: '',
    description: '',
    cities: '',
    occasion: ''
  });

  const [currentFlower, setCurrentFlower] = useState({
    name: '',
    quantity: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const [showFlowerSuggestions, setShowFlowerSuggestions] = useState(false);

  // Функция для форматирования цены
  const formatPrice = (value) => {
    // Удаляем все нецифровые символы
    const numbers = value.replace(/\D/g, '');
    // Добавляем разделители тысяч
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  };

  // Обработка ввода цены
  const handlePriceChange = (e) => {
    const formattedValue = formatPrice(e.target.value);
    setFormData({ ...formData, price: formattedValue });
  };

  // Обработка ввода только цифр
  const handleNumericInput = (field, value) => {
    const numericValue = value.replace(/\D/g, '');
    setFormData({ ...formData, [field]: numericValue });
  };

  // Переключение цвета
  const toggleColor = (colorId) => {
    const newColors = formData.selectedColors.includes(colorId)
      ? formData.selectedColors.filter(id => id !== colorId)
      : [...formData.selectedColors, colorId];
    setFormData({ ...formData, selectedColors: newColors });
  };

  // Добавление цветка в состав
  const addFlower = () => {
    if (currentFlower.name && currentFlower.quantity) {
      const newFlower = {
        id: Date.now(),
        name: currentFlower.name,
        quantity: parseInt(currentFlower.quantity) || 0
      };
      setFormData({
        ...formData,
        flowers: [...formData.flowers, newFlower]
      });
      setCurrentFlower({ name: '', quantity: '' });
      setShowFlowerSuggestions(false);
    }
  };

  // Удаление цветка из состава
  const removeFlower = (flowerId) => {
    setFormData({
      ...formData,
      flowers: formData.flowers.filter(f => f.id !== flowerId)
    });
  };

  // Фильтрация предложений цветов
  const getFlowerSuggestions = () => {
    if (!currentFlower.name) return [];
    return availableFlowers.filter(flower =>
      flower.toLowerCase().includes(currentFlower.name.toLowerCase())
    );
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;

    try {
      setIsSubmitting(true);
      setSubmitError(null);

      // Validate required fields
      if (!formData.name.trim()) {
        throw new Error('Название товара обязательно');
      }
      if (!formData.price.trim()) {
        throw new Error('Цена товара обязательна');
      }

      // Transform form data to API format
      const productData = {
        name: formData.name.trim(),
        price: Math.round(parseFloat(formData.price.replace(/[^\d.]/g, '')) * 100), // Convert to kopecks
        type: formData.category === 'Готовые букеты' ? 'flowers' :
              formData.category === 'Сладости' ? 'sweets' :
              formData.category === 'Фрукты' ? 'fruits' : 'flowers',
        description: formData.description.trim() || `Красивый ${formData.name}`,
        manufacturingTime: parseInt(formData.manufacturingTime) || 30,
        width: parseInt(formData.width) || null,
        height: parseInt(formData.height) || null,
        shelfLife: parseInt(formData.shelfLife) || null,
        enabled: true,
        is_featured: false,
        colors: formData.selectedColors,
        occasions: formData.occasion ? [formData.occasion] : [],
        cities: formData.cities ? formData.cities.split(',').map(city => city.trim()) : ['almaty'],
        image: formData.photos[0] || 'https://placehold.co/400x400/FF6666/FFFFFF?text=Фото' // Use uploaded photo or placeholder
      };

      console.log('Creating product:', productData);
      const result = await productsAPI.createProduct(productData);
      console.log('Product created successfully:', result);

      // Save all uploaded photos to ProductImage table
      if (formData.photos && formData.photos.length > 0) {
        console.log(`Saving ${formData.photos.length} photos to ProductImage...`);
        for (let i = 0; i < formData.photos.length; i++) {
          const photoUrl = formData.photos[i];
          try {
            await fetch(`${API_BASE_URL}/products/${result.id}/images`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                product_id: result.id,
                url: photoUrl,
                order: i,
                is_primary: i === 0
              })
            });
            console.log(`Photo ${i + 1}/${formData.photos.length} saved`);
          } catch (photoError) {
            console.error(`Failed to save photo ${i + 1}:`, photoError);
          }
        }
      }

      // Success - navigate back to main page
      navigate('/');
    } catch (err) {
      console.error('Failed to create product:', err);
      setSubmitError(err.message || 'Не удалось создать товар');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="figma-container bg-white">
      {/* Заголовок */}
      <div className="flex items-center justify-between px-4 py-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Новый товар</h1>
        <button
          onClick={() => navigate('/')}
          className="w-5 h-5 flex items-center justify-center"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 5L5 15M5 5L15 15" className="stroke-black" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      {/* Фото товара */}
      <ProductImageUpload
        images={formData.photos}
        onImagesChange={(urls) => setFormData({ ...formData, photos: urls })}
        maxImages={10}
      />

      {/* Категория */}
      <div className="px-4 py-3 border-b border-gray-border">
        <p className="text-[13px] text-gray-disabled font-['Open_Sans'] mb-2">Категория</p>
        <div className="flex items-center justify-between">
          <p className="text-base font-['Open_Sans']">{formData.category}</p>
          <button className="text-purple-primary text-sm font-['Open_Sans']">Изменить</button>
        </div>
      </div>

      {/* Название товара */}
      <div className="px-4 py-3 border-b border-gray-border">
        <input
          type="text"
          placeholder="Название товара"
          className="w-full text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          maxLength="100"
        />
        <p className="text-xs text-gray-disabled mt-1">Текстовое поле, максимум 100 символов</p>
      </div>

      {/* Стоимость товара */}
      <div className="px-4 py-3 border-b border-gray-border">
        <div className="flex items-center">
          <input
            type="text"
            inputMode="numeric"
            placeholder="Стоимость товара"
            className="flex-1 text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
            value={formData.price}
            onChange={handlePriceChange}
          />
          <span className="text-base font-['Open_Sans'] ml-2">₸</span>
        </div>
        <p className="text-xs text-gray-disabled mt-1">Только цифры</p>
      </div>

      {/* Время изготовления */}
      <div className="px-4 py-3 border-b border-gray-border">
        <div className="flex items-center">
          <input
            type="text"
            inputMode="numeric"
            placeholder="Время изготовления"
            className="flex-1 text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
            value={formData.manufacturingTime}
            onChange={(e) => handleNumericInput('manufacturingTime', e.target.value)}
            maxLength="3"
          />
          <span className="text-base font-['Open_Sans'] ml-2">мин</span>
        </div>
        <p className="text-xs text-gray-disabled mt-1">Только цифры, в минутах</p>
      </div>

      {/* Состав букета */}
      <div className="px-4 py-4">
        <h2 className="text-xl font-['Open_Sans'] mb-4">Состав букета</h2>

        {/* Список добавленных цветов */}
        {formData.flowers.length > 0 && (
          <div className="mb-4 space-y-2">
            {formData.flowers.map((flower) => (
              <div key={flower.id} className="flex items-center justify-between bg-background-hover p-3 rounded">
                <span className="text-base font-['Open_Sans']">{flower.name}</span>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-disabled">{flower.quantity} шт</span>
                  <button
                    onClick={() => removeFlower(flower.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Поля для добавления цветов */}
        <div className="relative">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Название цветка"
                className="w-full pb-2 border-b border-gray-border text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
                value={currentFlower.name}
                onChange={(e) => {
                  setCurrentFlower({ ...currentFlower, name: e.target.value });
                  setShowFlowerSuggestions(true);
                }}
                onFocus={() => setShowFlowerSuggestions(true)}
              />

              {/* Выпадающий список предложений */}
              {showFlowerSuggestions && getFlowerSuggestions().length > 0 && (
                <div className="absolute top-full left-0 right-0 bg-white border border-gray-border rounded-b shadow-lg z-10 max-h-40 overflow-y-auto">
                  {getFlowerSuggestions().map((flower) => (
                    <div
                      key={flower}
                      className="px-3 py-2 hover:bg-background-hover cursor-pointer text-sm font-['Open_Sans']"
                      onClick={() => {
                        setCurrentFlower({ ...currentFlower, name: flower });
                        setShowFlowerSuggestions(false);
                      }}
                    >
                      {flower}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <input
              type="text"
              inputMode="numeric"
              placeholder="Количество, шт"
              className="flex-1 pb-2 border-b border-gray-border text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
              value={currentFlower.quantity}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '');
                setCurrentFlower({ ...currentFlower, quantity: value });
              }}
              maxLength="3"
            />
          </div>
        </div>

        {/* Кнопка добавления цветка */}
        <button
          onClick={addFlower}
          className="w-full py-3 border border-border-input rounded text-base font-['Open_Sans'] tracking-wider uppercase hover:bg-background-hover transition-colors"
        >
          + Добавить цветок
        </button>

        <p className="text-xs text-gray-disabled mt-2">В будущем список цветов будет загружаться со склада</p>
      </div>

      {/* Характеристики */}
      <div className="px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-['Open_Sans']">Характеристики</h2>
          <svg width="12" height="6" viewBox="0 0 12 6" fill="none" className="transform rotate-180">
            <path d="M1 1L6 5L11 1" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>

        {/* Цвета букета - теги */}
        <div className="py-3 border-b border-gray-border">
          <p className="text-sm text-gray-disabled font-['Open_Sans'] mb-3">Цвета букета</p>
          <div className="flex flex-wrap gap-2">
            {availableColors.map((color) => (
              <button
                key={color.id}
                onClick={() => toggleColor(color.id)}
                className={`px-3 py-1.5 rounded-full text-sm font-['Open_Sans'] transition-all ${
                  formData.selectedColors.includes(color.id)
                    ? 'ring-2 ring-[#8A49F3] ring-offset-1'
                    : ''
                }`}
                style={{
                  background: color.color,
                  color: color.id === 'white' ? '#333' : '#fff',
                  border: color.border ? '1px solid #E0E0E0' : 'none'
                }}
              >
                {color.name}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-disabled mt-2">Выберите один или несколько цветов</p>
        </div>

        {/* Размеры */}
        <div className="flex gap-4 py-3 border-b border-gray-border">
          <div className="flex-1">
            <div className="flex items-center">
              <input
                type="text"
                inputMode="numeric"
                placeholder="Ширина"
                className="flex-1 text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
                value={formData.width}
                onChange={(e) => handleNumericInput('width', e.target.value)}
                maxLength="3"
              />
              <span className="text-sm text-gray-disabled ml-1">см</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center">
              <input
                type="text"
                inputMode="numeric"
                placeholder="Высота"
                className="flex-1 text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
                value={formData.height}
                onChange={(e) => handleNumericInput('height', e.target.value)}
                maxLength="3"
              />
              <span className="text-sm text-gray-disabled ml-1">см</span>
            </div>
          </div>
        </div>

        {/* Сколько простоит */}
        <div className="py-3 border-b border-gray-border">
          <div className="flex items-center">
            <input
              type="text"
              inputMode="numeric"
              placeholder="Сколько простоит"
              className="flex-1 text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
              value={formData.shelfLife}
              onChange={(e) => handleNumericInput('shelfLife', e.target.value)}
              maxLength="2"
            />
            <span className="text-sm text-gray-disabled ml-2">дней</span>
          </div>
          <p className="text-xs text-gray-disabled mt-1">Укажите количество дней</p>
        </div>
      </div>

      {/* Дополнительная информация */}
      <div className="px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-['Open_Sans']">Дополнительная информация</h2>
          <svg width="12" height="6" viewBox="0 0 12 6" fill="none" className="transform rotate-180">
            <path d="M1 1L6 5L11 1" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>

        {/* Описание товара */}
        <div className="py-3 border-b border-gray-border">
          <textarea
            placeholder="Описание товара"
            className="w-full text-base font-['Open_Sans'] placeholder-gray-disabled outline-none resize-none"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows="3"
            maxLength="500"
          />
          <p className="text-xs text-gray-disabled mt-1">Максимум 500 символов</p>
        </div>

        {/* Доступен в городах */}
        <div className="py-3 border-b border-gray-border">
          <input
            type="text"
            placeholder="Доступен в городах"
            className="w-full text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
            value={formData.cities}
            onChange={(e) => setFormData({ ...formData, cities: e.target.value })}
          />
          <p className="text-xs text-gray-disabled mt-1">Например: Алматы, Астана, Караганда</p>
        </div>

        {/* Повод */}
        <div className="py-3 border-b border-gray-border">
          <input
            type="text"
            placeholder="Повод"
            className="w-full text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
            value={formData.occasion}
            onChange={(e) => setFormData({ ...formData, occasion: e.target.value })}
          />
          <p className="text-xs text-gray-disabled mt-1">Например: День рождения, Свадьба, 8 Марта</p>
        </div>
      </div>

      {/* Кнопка публикации */}
      <div className="px-4 py-6">
        {submitError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-red-600 text-sm">{submitError}</p>
          </div>
        )}
        <button
          onClick={handleSubmit}
          className="w-full py-3 bg-purple-primary text-white rounded text-base font-['Open_Sans'] tracking-wider uppercase hover:bg-purple-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!formData.name || !formData.price || isSubmitting}
        >
          {isSubmitting ? 'Создание товара...' : 'Опубликовать'}
        </button>
        <p className="text-xs text-gray-disabled text-center mt-2">
          Обязательные поля: название и стоимость
        </p>
      </div>
    </div>
  );
};

export default AddProduct;