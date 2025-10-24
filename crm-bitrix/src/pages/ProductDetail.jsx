import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productsAPI } from '../services';
import LoadingSpinner from '../components/LoadingSpinner';
import PriceFormatter from '../components/PriceFormatter';
import { useToast } from '../components/ToastProvider';
import { ArrowLeft } from 'lucide-react';

export function ProductDetail() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { showError } = useToast();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProduct();
  }, [productId]);

  async function loadProduct() {
    try {
      setLoading(true);
      const data = await productsAPI.getProduct(productId);
      setProduct(data);
      setError(null);
    } catch (err) {
      const message = err.message || 'Ошибка при загрузке товара';
      setError(message);
      showError(message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <LoadingSpinner message="Загрузка товара..." />;

  if (error || !product) {
    return (
      <div className="figma-container bg-white flex items-center justify-center">
        <div className="p-6 text-center">
          <h2 className="text-lg font-sans font-bold text-red-600 mb-2">Ошибка</h2>
          <p className="text-gray-disabled mb-4">{error || 'Товар не найден'}</p>
          <button
            onClick={() => navigate('/products')}
            className="w-full bg-purple-primary hover:bg-purple-hover text-white py-2 rounded-lg transition font-sans"
          >
            Вернуться к товарам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6 px-4 mt-4">
        <button
          onClick={() => navigate('/products')}
          className="p-2 hover:bg-gray-input rounded-lg transition"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-2xl font-sans font-normal">{product.name}</h1>
      </div>

      {/* Product Image */}
      {product.image && (
        <div className="px-4 mb-6">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-96 object-cover rounded"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        </div>
      )}

      {/* Product Info */}
      <div className="px-4 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Цена</p>
            <PriceFormatter price={product.price} size="lg" />
          </div>
          <span className={`px-3 py-1 rounded-lg text-sm font-sans font-medium ${
            product.enabled
              ? 'bg-status-green text-white'
              : 'bg-status-new text-white'
          }`}>
            {product.enabled ? 'Доступен' : 'Недоступен'}
          </span>
        </div>

        {product.type && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Тип товара</p>
            <p className="font-sans">{product.type}</p>
          </div>
        )}

        {product.description && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Описание</p>
            <p className="font-sans">{product.description}</p>
          </div>
        )}

        {product.width && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Ширина</p>
            <p className="font-sans">{product.width}</p>
          </div>
        )}

        {product.height && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Высота</p>
            <p className="font-sans">{product.height}</p>
          </div>
        )}

        {product.manufacturing_time && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Время производства</p>
            <p className="font-sans">{product.manufacturing_time}</p>
          </div>
        )}

        {product.variants && product.variants.length > 0 && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-2 font-sans">Доступные размеры</p>
            <div className="space-y-2">
              {product.variants.map((variant) => (
                <div key={variant.id ?? variant.size} className="flex justify-between font-sans">
                  <span>{variant.size}</span>
                  <PriceFormatter variant="inline" price={variant.price} />
                </div>
              ))}
            </div>
          </div>
        )}

        {product.addons && product.addons.length > 0 && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-2 font-sans">Дополнительные опции</p>
            <ul className="space-y-2 font-sans">
              {product.addons.map((addon) => (
                <li key={addon.id ?? addon.name} className="flex justify-between items-center">
                  <span>{addon.name}</span>
                  <PriceFormatter variant="inline" price={addon.price} />
                </li>
              ))}
            </ul>
          </div>
        )}

        {product.composition && product.composition.length > 0 && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-2 font-sans">Состав</p>
            <ul className="space-y-1 font-sans">
              {product.composition.map((item) => (
                <li key={item.id}>
                  {item.name} — {item.quantity} шт.
                </li>
              ))}
            </ul>
          </div>
        )}

        {product.pickup_locations && product.pickup_locations.length > 0 && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-2 font-sans">Пункты самовывоза</p>
            <ul className="space-y-1 font-sans">
              {product.pickup_locations.map((location, index) => (
                <li key={`${location}-${index}`}>{location}</li>
              ))}
            </ul>
          </div>
        )}

        {product.frequently_bought && product.frequently_bought.length > 0 && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-2 font-sans">Часто покупают вместе</p>
            <ul className="space-y-2 font-sans">
              {product.frequently_bought.map((item) => (
                <li key={item.id} className="flex justify-between items-center">
                  <span>{item.name}</span>
                  <PriceFormatter variant="inline" price={item.price} />
                </li>
              ))}
            </ul>
          </div>
        )}

        {product.colors && product.colors.length > 0 && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Цвета</p>
            <p className="font-sans">{product.colors.join(', ')}</p>
          </div>
        )}

        {product.created_at && (
          <div className="border-t border-gray-border pt-4 mt-4">
            <p className="text-sm text-gray-placeholder mb-1 font-sans">Дата создания</p>
            <p className="font-sans">
              {new Date(product.created_at).toLocaleString('ru-RU')}
            </p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="px-4 pb-8">
        <button
          onClick={() => navigate(`/products/${product.id}/edit`)}
          className="w-full px-4 py-2 bg-purple-primary hover:bg-purple-hover text-white rounded-lg transition font-sans font-medium"
        >
          Редактировать
        </button>
      </div>
    </div>
  );
}

export default ProductDetail;
