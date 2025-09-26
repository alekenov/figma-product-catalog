import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './App.css';

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
        // Загрузка товара
        const productResponse = await fetch(`http://localhost:8014/api/v1/products/${id}`);
        if (!productResponse.ok) throw new Error('Product not found');
        const productData = await productResponse.json();

        // Загрузка рецептуры
        const recipeResponse = await fetch(`http://localhost:8014/api/v1/products/${id}/recipe`);
        const recipeData = await recipeResponse.json();

        // Загрузка складских позиций
        const warehouseResponse = await fetch('http://localhost:8014/api/v1/warehouse/');
        const warehouseData = await warehouseResponse.json();

        setFormData({
          ...productData,
          manufacturingTime: productData.manufacturingTime || '',
          width: productData.width || '',
          height: productData.height || '',
          shelfLife: productData.shelfLife || '',
          photos: productData.image ? [productData.image] : [],
          video: '',
          category: productData.type || 'flowers',
          cities: productData.cities?.join(', ') || '',
          recipient: '',
          occasion: productData.occasions?.join(', ') || '',
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
        setTotalCost(recipeData.total_cost || 0);
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

  const handleRemovePhoto = (index) => {
    setFormData(prev => ({
      ...prev,
      photos: prev.photos.filter((_, i) => i !== index)
    }));
  };

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
        return sum + (recipe.warehouse_item.cost_price * parseInt(recipe.quantity));
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
        return sum + (recipe.warehouse_item.cost_price * parseInt(recipe.quantity));
      }
      return sum;
    }, 0);

    setTotalCost(newTotalCost);
  };

  const handleSave = async () => {
    try {
      // Сохранение данных товара
      const productResponse = await fetch(`http://localhost:8014/api/v1/products/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          price: parseInt(formData.price),
          description: formData.description,
          manufacturingTime: parseInt(formData.manufacturingTime) || null,
          width: parseInt(formData.width) || null,
          height: parseInt(formData.height) || null,
          shelfLife: parseInt(formData.shelfLife) || null,
          image: formData.photos[0] || null,
          colors: formData.colors,
          cities: formData.cities?.split(', ').filter(c => c),
          occasions: formData.occasion?.split(', ').filter(o => o)
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

      await fetch(`http://localhost:8014/api/v1/products/${id}/recipe/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recipeData)
      });

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
      <div className="px-4 py-4">
        <h2 className="text-base font-['Open_Sans'] mb-3">Фото</h2>
        <div className="flex gap-2 overflow-x-auto">
          {formData.photos.map((photo, index) => (
            <div key={index} className="relative">
              <img src={photo} alt="" className="w-20 h-20 rounded object-cover" />
              <button
                onClick={() => handleRemovePhoto(index)}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs"
              >
                ×
              </button>
            </div>
          ))}
          <button className="w-20 h-20 border-2 border-dashed border-gray-300 rounded flex items-center justify-center">
            <span className="text-2xl text-gray-400">+</span>
          </button>
        </div>
      </div>

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
                <select
                  className="w-full pb-2 border-b border-[#E0E0E0] text-base font-['Open_Sans'] outline-none"
                  value={recipe.warehouse_item_id}
                  onChange={(e) => handleRecipeChange(index, 'warehouse_item_id', e.target.value)}
                >
                  <option value="">Выберите компонент</option>
                  {warehouseItems.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.name} (остаток: {item.quantity} шт, {item.cost_price} ₸/шт)
                    </option>
                  ))}
                </select>
              </div>
              <input
                type="number"
                placeholder="Кол-во"
                className="w-20 pb-2 border-b border-[#E0E0E0] text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none text-center"
                value={recipe.quantity}
                onChange={(e) => handleRecipeChange(index, 'quantity', e.target.value)}
                min="1"
              />
              <button
                onClick={() => handleRemoveRecipeItem(index)}
                className="w-6 h-6 text-red-500 text-xl"
              >
                ×
              </button>
            </div>

            {recipe.warehouse_item && (
              <div className="mt-2 text-sm text-gray-600">
                Себестоимость: {recipe.warehouse_item.cost_price * recipe.quantity} ₸
                {recipe.warehouse_item.quantity < recipe.quantity && (
                  <span className="ml-2 text-red-500">⚠️ Недостаточно на складе</span>
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
          <div className="mt-4 p-3 bg-gray-100 rounded">
            <div className="flex justify-between items-center">
              <span className="font-['Open_Sans'] text-base">Общая себестоимость:</span>
              <span className="font-['Open_Sans'] text-base font-bold">{totalCost} ₸</span>
            </div>
            {formData.price && (
              <div className="flex justify-between items-center mt-2">
                <span className="font-['Open_Sans'] text-base">Маржа:</span>
                <span className="font-['Open_Sans'] text-base font-bold text-green-600">
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

        {/* Цвета букета */}
        <div className="py-3 border-b border-[#E0E0E0]">
          <input
            type="text"
            placeholder="Цвета букета"
            className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
            value={formData.colors?.join(', ') || ''}
            onChange={(e) => setFormData({ ...formData, colors: e.target.value.split(', ') })}
          />
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

        {/* Сколько простоит */}
        <div className="py-3 border-b border-[#E0E0E0]">
          <input
            type="text"
            placeholder="Сколько простоит"
            className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
            value={formData.shelfLife}
            onChange={(e) => setFormData({ ...formData, shelfLife: e.target.value })}
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

      {/* Города */}
      <div className="px-4 py-3 border-t border-[#E0E0E0]">
        <input
          type="text"
          placeholder="Города (через запятую)"
          className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
          value={formData.cities}
          onChange={(e) => setFormData({ ...formData, cities: e.target.value })}
        />
      </div>

      {/* Поводы */}
      <div className="px-4 py-3 border-t border-[#E0E0E0]">
        <input
          type="text"
          placeholder="Поводы (через запятую)"
          className="w-full text-base font-['Open_Sans'] placeholder-[#6B6773] outline-none"
          value={formData.occasion}
          onChange={(e) => setFormData({ ...formData, occasion: e.target.value })}
        />
      </div>
    </div>
  );
};

export default EditProduct;