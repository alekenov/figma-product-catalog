import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './App.css';
import { API_BASE_URL, authenticatedFetch } from './services/api';
import ProductImageUpload from './components/ProductImageUpload';
import IngredientSelector from './components/IngredientSelector';
import { BOUQUET_COLORS } from './utils/colors';

const EditProduct = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [formData, setFormData] = useState(null);
  const [warehouseItems, setWarehouseItems] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [totalCost, setTotalCost] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загрузка данных товара, рецептуры и складских позиций
    const fetchData = async () => {
      try {
        // Загрузка товара (базовая информация)
        const productResponse = await authenticatedFetch(`${API_BASE_URL}/products/${id}`);
        if (!productResponse.ok) throw new Error('Product not found');
        const productData = await productResponse.json();

        // Загрузка фото из detail endpoint
        const detailResponse = await authenticatedFetch(`${API_BASE_URL}/products/${id}/detail`);
        const detailData = await detailResponse.json();

        // Загрузка рецептуры
        const recipeResponse = await authenticatedFetch(`${API_BASE_URL}/products/${id}/recipe`);
        const recipeData = await recipeResponse.json();

        // Загрузка складских позиций
        const warehouseResponse = await authenticatedFetch(`${API_BASE_URL}/warehouse/`);
        const warehouseData = await warehouseResponse.json();

        // Преобразуем названия цветов в ID для UI
        const selectedColorIds = (productData.colors || [])
          .map(colorName => BOUQUET_COLORS.find(c => c.name === colorName)?.id)
          .filter(Boolean);

        setFormData({
          ...productData,
          price: Math.floor(productData.price / 100),  // Convert kopecks to tenge for display
          manufacturingTime: productData.manufacturingTime || '',
          width: productData.width || '',
          height: productData.height || '',
          photos: detailData.images?.map(img => img.url) || [],
          selectedColors: selectedColorIds,
          video: '',
          recipient: '',
          tags: []
        });

        // Преобразуем рецептуру
        const recipesWithDetails = recipeData.recipes?.map(recipe => ({
          id: recipe.id,
          warehouse_item_id: recipe.warehouse_item_id,
          warehouse_item: recipe.warehouse_item,
          quantity: recipe.quantity,
          is_optional: recipe.is_optional
        })) || [];

        setRecipes(recipesWithDetails);
        setTotalCost(Math.floor((recipeData.total_cost || 0) / 100)); // Конвертируем копейки → тенге
        setWarehouseItems(warehouseData);
      } catch (error) {
        console.error('Error loading data:', error);
        navigate('/');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, navigate]);

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

  // Переключение цвета
  const toggleColor = (colorId) => {
    const newColors = formData.selectedColors.includes(colorId)
      ? formData.selectedColors.filter(id => id !== colorId)
      : [...formData.selectedColors, colorId];
    setFormData({ ...formData, selectedColors: newColors });
  };

  const handleSave = async () => {
    try {
      // Сохранение данных товара
      const productResponse = await authenticatedFetch(`${API_BASE_URL}/products/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          price: parseInt(formData.price) * 100,  // Convert tenge to kopecks
          description: formData.description,
          manufacturingTime: parseInt(formData.manufacturingTime) || null,
          width: parseInt(formData.width) || null,
          height: parseInt(formData.height) || null,
          image: formData.photos[0] || null,
          // Преобразуем ID обратно в названия для БД: ["Красный", "Розовый"]
          colors: (formData.selectedColors || [])
            .map(id => BOUQUET_COLORS.find(c => c.id === id)?.name)
            .filter(Boolean)
        })
      });

      if (!productResponse.ok) throw new Error('Failed to save product');

      // Сохранение рецептуры
      const recipeData = recipes
        .filter(r => r.warehouse_item_id)
        .map(r => ({
          warehouse_item_id: parseInt(r.warehouse_item_id),
          quantity: parseInt(r.quantity),
          is_optional: r.is_optional
        }));

      await authenticatedFetch(`${API_BASE_URL}/products/${id}/recipe/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recipeData)
      });

      // Sync photos with ProductImage table
      // Step 1: Get existing images
      const existingImagesResponse = await authenticatedFetch(`${API_BASE_URL}/products/${id}/detail`);
      const existingImagesData = await existingImagesResponse.json();
      const existingImages = existingImagesData.images || [];

      // Step 2: Delete all existing images
      console.log(`Deleting ${existingImages.length} existing photos...`);
      for (const img of existingImages) {
        try {
          await authenticatedFetch(`${API_BASE_URL}/products/${id}/images/${img.id}`, {
            method: 'DELETE'
          });
        } catch (deleteError) {
          console.error(`Failed to delete image ${img.id}:`, deleteError);
        }
      }

      // Step 3: Create new images for all current photos
      if (formData.photos && formData.photos.length > 0) {
        console.log(`Saving ${formData.photos.length} photos to ProductImage...`);
        for (let i = 0; i < formData.photos.length; i++) {
          const photoUrl = formData.photos[i];
          try {
            await authenticatedFetch(`${API_BASE_URL}/products/${id}/images`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                product_id: parseInt(id),
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

      alert('Товар успешно сохранен!');
      navigate('/');
    } catch (error) {
      console.error('Error saving product:', error);
      alert('Ошибка при сохранении товара');
    }
  };

  if (loading) {
    return (
      <div className="figma-container">
        <div className="flex justify-center items-center h-screen">
          <div>Загрузка...</div>
        </div>
      </div>
    );
  }

  if (!formData) {
    return null;
  }

  return (
    <div className="figma-container bg-white min-h-screen">
      {/* Header - matching ProductDetail style */}
      <div className="bg-white border-b border-gray-border px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="w-6 h-6 flex items-center justify-center"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <h1 className="text-xl font-['Open_Sans']">Редактировать товар</h1>
        </div>
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-purple-primary text-white rounded font-['Open_Sans'] font-semibold"
        >
          Сохранить
        </button>
      </div>

      {/* Название и цена */}
      <div className="px-4 py-3 border-b border-[#E0E0E0]">
        <input
          type="text"
          placeholder="Название товара"
          className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none mb-3"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        <input
          type="text"
          placeholder="Цена"
          className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
          value={formData.price}
          onChange={(e) => setFormData({ ...formData, price: e.target.value })}
        />
      </div>

      {/* Фото */}
      <ProductImageUpload
        images={formData.photos}
        onImagesChange={(urls) => setFormData({ ...formData, photos: urls })}
        maxImages={10}
      />

      {/* Время изготовления */}
      <div className="px-4 py-3 border-b border-[#E0E0E0]">
        <div className="flex items-center justify-between">
          <input
            type="text"
            placeholder="Время изготовления"
            className="flex-1 text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
            value={formData.manufacturingTime}
            onChange={(e) => setFormData({ ...formData, manufacturingTime: e.target.value })}
          />
          <div className="flex items-center ml-4">
            <span className="text-base font-['Open_Sans'] mr-2">Мин</span>
          </div>
        </div>
      </div>

      {/* Состав букета (Рецептура) */}
      <div className="px-4 py-4 border-b border-[#E0E0E0]">
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
                className="w-16 pb-2 border-b border-[#E0E0E0] text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none text-center"
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
          className="w-full py-3 border border-[#E2E2E2] rounded text-base font-['Open_Sans'] tracking-wider uppercase"
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
                <span className="font-['Open_Sans'] text-xl font-bold text-green-600">
                  {((1 - totalCost / parseInt(formData.price)) * 100).toFixed(1)}%
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
        </div>

        {/* Цвета букета - теги */}
        <div className="py-3 border-b border-[#E0E0E0]">
          <p className="text-sm text-gray-disabled font-['Open_Sans'] mb-3">Цвета букета</p>
          <div className="flex flex-wrap gap-2">
            {BOUQUET_COLORS.map((color) => (
              <button
                key={color.id}
                onClick={() => toggleColor(color.id)}
                type="button"
                className={`px-3 py-1.5 rounded-full text-sm font-['Open_Sans'] transition-all ${
                  formData.selectedColors?.includes(color.id)
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
        <div className="flex gap-4 py-3 border-b border-[#E0E0E0]">
          <input
            type="text"
            placeholder="Ширина, см"
            className="flex-1 text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
            value={formData.width}
            onChange={(e) => setFormData({ ...formData, width: e.target.value })}
          />
          <input
            type="text"
            placeholder="Высота, см"
            className="flex-1 text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
            value={formData.height}
            onChange={(e) => setFormData({ ...formData, height: e.target.value })}
          />
        </div>

        {/* Описание */}
        <div className="py-3">
          <textarea
            placeholder="Описание"
            className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none resize-none"
            rows="3"
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>
      </div>

    </div>
  );
};

export default EditProduct;
