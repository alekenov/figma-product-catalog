import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsAPI, API_BASE_URL, authenticatedFetch } from './services';
import { useCreateProduct } from './hooks/useProducts';
import ProductImageUpload from './components/ProductImageUpload';
import IngredientSelector from './components/IngredientSelector';
import { BOUQUET_COLORS } from './utils/colors';
import './App.css';

const AddProduct = () => {
  const navigate = useNavigate();
  const createProduct = useCreateProduct();

  // Складские позиции (загружаются из API)
  const [warehouseItems, setWarehouseItems] = useState([]);

  const [formData, setFormData] = useState({
    photos: [],
    name: '',
    price: '',
    manufacturingTime: '',
    selectedColors: [],
    width: '',
    height: '',
    description: ''
  });

  const [recipes, setRecipes] = useState([]);
  const [totalCost, setTotalCost] = useState(0);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Загрузка складских позиций при монтировании компонента
  useEffect(() => {
    const fetchWarehouseItems = async () => {
      try {
        const response = await authenticatedFetch(`${API_BASE_URL}/warehouse/`);
        if (response.ok) {
          const data = await response.json();
          setWarehouseItems(data);
          console.log('Loaded warehouse items:', data.length);
        } else {
          console.error('Failed to load warehouse items:', response.status);
        }
      } catch (error) {
        console.error('Failed to load warehouse items:', error);
      }
    };

    fetchWarehouseItems();
  }, []);

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

  // Управление рецептурой
  const handleAddRecipeItem = () => {
    setRecipes(prev => [...prev, {
      warehouse_item_id: '',
      quantity: 1,
      is_optional: false,
      warehouse_item: null
    }]);
  };

  const handleRecipeChange = (index, field, value) => {
    const updatedRecipes = [...recipes];

    if (field === 'warehouse_item_id') {
      const selectedItem = warehouseItems.find(item => item.id === parseInt(value));
      updatedRecipes[index] = {
        ...updatedRecipes[index],
        warehouse_item_id: value,
        warehouse_item: selectedItem
      };
    } else {
      updatedRecipes[index] = {
        ...updatedRecipes[index],
        [field]: value
      };
    }

    setRecipes(updatedRecipes);

    // Пересчитать общую стоимость
    const newTotalCost = updatedRecipes.reduce((sum, recipe) => {
      if (recipe.warehouse_item && recipe.quantity) {
        return sum + (Math.floor(recipe.warehouse_item.cost_price / 100) * parseInt(recipe.quantity));
      }
      return sum;
    }, 0);

    setTotalCost(newTotalCost);
  };

  const handleRemoveRecipeItem = (index) => {
    const updatedRecipes = recipes.filter((_, i) => i !== index);
    setRecipes(updatedRecipes);

    // Пересчитать общую стоимость
    const newTotalCost = updatedRecipes.reduce((sum, recipe) => {
      if (recipe.warehouse_item && recipe.quantity) {
        return sum + (Math.floor(recipe.warehouse_item.cost_price / 100) * parseInt(recipe.quantity));
      }
      return sum;
    }, 0);

    setTotalCost(newTotalCost);
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
        type: 'flowers',
        description: formData.description.trim() || `Красивый ${formData.name}`,
        manufacturingTime: parseInt(formData.manufacturingTime) || 30,
        width: parseInt(formData.width) || null,
        height: parseInt(formData.height) || null,
        enabled: true,
        is_featured: false,
        // Сохраняем названия цветов для ИИ/MCP: ["Красный", "Розовый"]
        colors: formData.selectedColors
          .map(id => BOUQUET_COLORS.find(c => c.id === id)?.name)
          .filter(Boolean),
        image: formData.photos[0] || 'https://placehold.co/400x400/FF6666/FFFFFF?text=Фото' // Use uploaded photo or placeholder
      };

      console.log('Creating product:', productData);

      // Use React Query mutation which automatically invalidates cache
      const result = await createProduct.mutateAsync(productData);
      console.log('Product created successfully:', result);

      // Save all uploaded photos to ProductImage table
      if (formData.photos && formData.photos.length > 0) {
        console.log(`Saving ${formData.photos.length} photos to ProductImage...`);
        for (let i = 0; i < formData.photos.length; i++) {
          const photoUrl = formData.photos[i];
          try {
            await authenticatedFetch(`${API_BASE_URL}/products/${result.id}/images`, {
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

      // Save recipe components (using batch endpoint)
      if (recipes && recipes.length > 0) {
        const validRecipes = recipes.filter(r => r.warehouse_item_id);
        if (validRecipes.length > 0) {
          console.log(`Saving ${validRecipes.length} recipe components...`);
          try {
            const recipeData = validRecipes.map(r => ({
              warehouse_item_id: parseInt(r.warehouse_item_id),
              quantity: parseInt(r.quantity),
              is_optional: r.is_optional
            }));

            const recipeResponse = await authenticatedFetch(
              `${API_BASE_URL}/products/${result.id}/recipe/batch`,
              {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(recipeData)
              }
            );

            if (recipeResponse.ok) {
              console.log(`${validRecipes.length} recipe components saved successfully`);
            } else {
              console.error('Failed to save recipe:', await recipeResponse.text());
            }
          } catch (recipeError) {
            console.error('Failed to save recipe:', recipeError);
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

      {/* Состав букета (Рецептура) */}
      <div className="px-4 py-4 border-b border-gray-border">
        <h2 className="text-xl font-['Open_Sans'] mb-4">Состав букета</h2>

        {/* Список компонентов */}
        {recipes.map((recipe, index) => (
          <div key={index} className="mb-4 pb-4 border-b border-gray-200 last:border-0">
            <div className="flex gap-2 items-start">
              <div className="flex-1">
                <IngredientSelector
                  warehouseItems={warehouseItems}
                  selectedItemId={recipe.warehouse_item_id}
                  onSelect={(itemId) => handleRecipeChange(index, 'warehouse_item_id', itemId)}
                  placeholder="Начните вводить название..."
                />
              </div>
              <input
                type="number"
                placeholder="Кол-во"
                className="w-16 pb-2 border-b border-gray-border text-base font-['Open_Sans'] placeholder-gray-disabled outline-none text-center"
                value={recipe.quantity}
                onChange={(e) => handleRecipeChange(index, 'quantity', e.target.value)}
                min="1"
                max="999"
              />
              <button
                onClick={() => handleRemoveRecipeItem(index)}
                className="w-6 h-6 text-red-500 text-xl"
              >
                ×
              </button>
            </div>

            {recipe.warehouse_item && (
              <div className="mt-2 p-3 bg-gray-input rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-['Open_Sans'] text-gray-disabled">Себестоимость строки:</span>
                  <span className="text-base font-['Open_Sans'] font-bold">{(Math.floor(recipe.warehouse_item.cost_price / 100) * recipe.quantity).toLocaleString()} ₸</span>
                </div>
                {recipe.warehouse_item.quantity < recipe.quantity && (
                  <div className="flex items-center gap-2 text-red-500 text-sm">
                    <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                    </svg>
                    <span>Недостаточно на складе (доступно: {recipe.warehouse_item.quantity} шт)</span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Кнопка добавления компонента */}
        <button
          onClick={handleAddRecipeItem}
          className="w-full py-3 border border-gray-border rounded text-base font-['Open_Sans'] tracking-wider uppercase"
        >
          + Добавить цветок
        </button>

        {/* Общая себестоимость */}
        {totalCost > 0 && (
          <div className="mt-4 p-4 bg-gray-100 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="font-['Open_Sans'] text-lg font-semibold">Общая себестоимость:</span>
              <span className="font-['Open_Sans'] text-xl font-bold">{totalCost} ₸</span>
            </div>
            {formData.price && (
              <div className="flex justify-between items-center mt-3">
                <span className="font-['Open_Sans'] text-lg font-semibold">Маржа:</span>
                <span className="font-['Open_Sans'] text-xl font-bold text-green-success">
                  {((1 - totalCost / parseFloat(formData.price.replace(/\s/g, ''))) * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>
        )}
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
            {BOUQUET_COLORS.map((color) => (
              <button
                key={color.id}
                onClick={() => toggleColor(color.id)}
                className={`px-3 py-1.5 rounded-full text-sm font-['Open_Sans'] transition-all ${
                  formData.selectedColors.includes(color.id)
                    ? 'ring-2 ring-[#8A49F3] ring-offset-1'
                    : ''
                }`}
                style={{
                  background: color.hex,
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