import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ToggleSwitch from './components/ToggleSwitch';
import SectionHeader from './components/SectionHeader';
import StatusBadge from './components/StatusBadge';
import { useToast } from './components/ToastProvider';
import { productsAPI, formatProductForDisplay } from './services/api';
import './App.css';

function ProductDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { showSuccess, showError } = useToast();

  const [product, setProduct] = useState(null);
  const [recipe, setRecipe] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalCost, setTotalCost] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchProductData();
  }, [id]);

  const fetchProductData = async () => {
    try {
      setLoading(true);

      // Загрузка данных товара
      const productResponse = await productsAPI.getProduct(id);
      const formattedProduct = formatProductForDisplay(productResponse);
      setProduct(formattedProduct);

      // Загрузка рецептуры
      try {
        const recipeResponse = await fetch(`http://localhost:8014/api/v1/products/${id}/recipe`);
        if (recipeResponse.ok) {
          const recipeData = await recipeResponse.json();
          // Handle both array and object with recipes property
          const recipes = Array.isArray(recipeData) ? recipeData : (recipeData.recipes || []);
          setRecipe(recipes);

          // Расчет общей себестоимости
          const cost = recipes.reduce((sum, item) => {
            return sum + (item.warehouse_item.cost_price * item.quantity);
          }, 0);
          setTotalCost(cost);
        }
      } catch (err) {
        console.error('Error fetching recipe:', err);
        // Recipe might not exist for all products
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching product:', err);
    } finally {
      setLoading(false);
    }
  };

  // Расчет маржи
  const calculateMargin = (cost, retail) => {
    if (retail === 0) return 0;
    return ((retail - cost) / retail * 100).toFixed(1);
  };

  // Расчет наценки
  const calculateMarkup = (cost, retail) => {
    if (cost === 0) return 0;
    return ((retail - cost) / cost * 100).toFixed(1);
  };

  const handleToggleStatus = async () => {
    try {
      await productsAPI.toggleProductStatus(id, !product.enabled);
      setProduct(prev => ({ ...prev, enabled: !prev.enabled }));
      showSuccess(product.enabled ? 'Товар деактивирован' : 'Товар активирован');
    } catch (err) {
      console.error('Error toggling product status:', err);
      showError('Ошибка при изменении статуса товара');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить этот товар?')) {
      return;
    }

    try {
      setIsDeleting(true);
      await productsAPI.deleteProduct(id);
      showSuccess('Товар успешно удален');
      navigate('/');
    } catch (err) {
      console.error('Error deleting product:', err);
      showError('Ошибка при удалении товара');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleEdit = () => {
    navigate(`/edit-product/${id}`);
  };

  const formatPrice = (price) => {
    return `${price.toLocaleString()} ₸`;
  };

  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder font-['Open_Sans']">Загрузка...</div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="figma-container bg-white">
        <div className="px-4 py-6">
          <div className="text-center py-8 text-red-500 font-['Open_Sans']">
            Ошибка: {error || 'Товар не найден'}
          </div>
          <button
            onClick={() => navigate('/')}
            className="w-full bg-purple-primary text-white py-3 rounded font-['Open_Sans'] uppercase tracking-wider"
          >
            Вернуться к каталогу
          </button>
        </div>
      </div>
    );
  }

  const margin = calculateMargin(totalCost, product.price);
  const markup = calculateMarkup(totalCost, product.price);

  return (
    <div className="figma-container bg-white">
      {/* Header */}
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
          <h1 className="text-xl font-['Open_Sans']">{product.name}</h1>
        </div>
        <StatusBadge
          status={product.enabled ? 'active' : 'inactive'}
          label={product.enabled ? 'Активен' : 'Неактивен'}
        />
      </div>

      {/* Product image and basic info */}
      <div className="px-4 pt-4 pb-6 flex items-center gap-3 border-b border-gray-border">
        <div className="relative w-[88px] h-[88px] flex-shrink-0">
          <img
            src={product.image || "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__"}
            alt={product.name}
            className="w-full h-full object-cover rounded"
          />
        </div>
        <div className="flex-1">
          <div className="text-sm font-['Open_Sans'] text-gray-disabled">Тип товара</div>
          <div className="text-base font-['Open_Sans'] text-black mb-2">
            {product.type === 'BOUQUET' ? 'Букет' : product.type === 'COMPOSITION' ? 'Композиция' : product.type}
          </div>
          <div className="text-sm font-['Open_Sans'] text-gray-disabled">Розничная цена</div>
          <div className="text-2xl font-['Open_Sans'] font-bold text-purple-primary">
            {formatPrice(product.price)}
          </div>
        </div>
      </div>

      {/* Pricing section */}
      <div className="px-4 py-6 border-b border-gray-border">
        <SectionHeader title="Ценообразование" />

        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Себестоимость</div>
              <div className="text-base font-['Open_Sans'] text-black">{formatPrice(totalCost)}</div>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Маржа</div>
              <div className="text-base font-['Open_Sans'] text-black">{margin}%</div>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Наценка</div>
              <div className="text-base font-['Open_Sans'] font-bold text-green-success">{markup}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recipe section */}
      {recipe.length > 0 && (
        <div className="px-4 py-6 border-b border-gray-border">
          <SectionHeader title="Рецептура" />

          <div className="space-y-3">
            {recipe.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="text-base font-['Open_Sans'] text-black">
                    {item.warehouse_item.name}
                  </div>
                  <div className="text-sm font-['Open_Sans'] text-gray-disabled">
                    {item.quantity} {item.warehouse_item.unit || 'шт'} × {formatPrice(item.warehouse_item.cost_price)}
                  </div>
                </div>
                <div className="text-base font-['Open_Sans'] text-black">
                  {formatPrice(item.warehouse_item.cost_price * item.quantity)}
                </div>
              </div>
            ))}

            <div className="pt-3 mt-3 border-t border-gray-border">
              <div className="flex justify-between items-center">
                <div className="text-base font-['Open_Sans'] font-bold text-black">Итого</div>
                <div className="text-base font-['Open_Sans'] font-bold text-black">{formatPrice(totalCost)}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Product details section */}
      <div className="px-4 py-6 border-b border-gray-border">
        <SectionHeader title="Характеристики" />

        <div className="space-y-3">
          {product.description && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Описание</div>
              <div className="text-base font-['Open_Sans'] text-black">{product.description}</div>
            </div>
          )}

          {product.manufacturingTime && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Время изготовления</div>
              <div className="text-base font-['Open_Sans'] text-black">{product.manufacturingTime} мин</div>
            </div>
          )}

          {(product.width || product.height) && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Размеры</div>
              <div className="text-base font-['Open_Sans'] text-black">
                {product.width && `${product.width} см`}
                {product.width && product.height && ' × '}
                {product.height && `${product.height} см`}
              </div>
            </div>
          )}

          {product.shelfLife && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Срок годности</div>
              <div className="text-base font-['Open_Sans'] text-black">{product.shelfLife} дней</div>
            </div>
          )}

          {product.colors && product.colors.length > 0 && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled">Цвета</div>
              <div className="flex flex-wrap gap-2 mt-2">
                {product.colors.map((color, index) => (
                  <div
                    key={index}
                    className="px-3 py-1 bg-gray-input rounded-full text-sm font-['Open_Sans'] text-black"
                  >
                    {color}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Settings section */}
      <div className="px-4 py-6 border-b border-gray-border">
        <SectionHeader title="Настройки" />

        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="text-base font-['Open_Sans'] text-black">Показывать в каталоге</div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mt-1">
              {product.enabled ? 'Товар виден покупателям' : 'Товар скрыт от покупателей'}
            </div>
          </div>
          <ToggleSwitch
            checked={product.enabled}
            onChange={handleToggleStatus}
            size="md"
          />
        </div>
      </div>

      {/* Action buttons */}
      <div className="px-4 py-6 space-y-3">
        <button
          onClick={handleEdit}
          className="w-full bg-purple-primary text-white py-3 rounded font-['Open_Sans'] uppercase tracking-wider hover:bg-purple-700 transition-colors"
        >
          Редактировать
        </button>

        <button
          onClick={() => navigate('/')}
          className="w-full bg-white border border-gray-border text-black py-3 rounded font-['Open_Sans'] uppercase tracking-wider hover:bg-gray-50 transition-colors"
        >
          Назад к каталогу
        </button>

        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="w-full bg-error-primary text-white py-3 rounded font-['Open_Sans'] uppercase tracking-wider hover:bg-red-600 transition-colors disabled:opacity-50"
        >
          {isDeleting ? 'Удаление...' : 'Удалить товар'}
        </button>
      </div>
    </div>
  );
}

export default ProductDetail;