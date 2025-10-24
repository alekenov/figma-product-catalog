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
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-lg font-semibold text-red-600 mb-2">Ошибка</h2>
          <p className="text-gray-700 mb-4">{error || 'Товар не найден'}</p>
          <button
            onClick={() => navigate('/products')}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition"
          >
            Вернуться к товарам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto p-4">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate('/products')}
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
        </div>

        {/* Product Image */}
        {product.image && (
          <div className="bg-white rounded-lg p-4 mb-6">
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-96 object-cover rounded-lg"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
        )}

        {/* Product Info */}
        <div className="bg-white rounded-lg p-6 space-y-4 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500 mb-1">Цена</p>
              <PriceFormatter price={product.price} size="lg" />
            </div>
            <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
              product.enabled
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {product.enabled ? 'Доступен' : 'Недоступен'}
            </span>
          </div>

          {product.type && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Тип товара</p>
              <p className="text-lg font-medium">{product.type}</p>
            </div>
          )}

          {product.description && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Описание</p>
              <p className="text-lg">{product.description}</p>
            </div>
          )}

          {product.width && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Ширина</p>
              <p className="text-lg">{product.width}</p>
            </div>
          )}

          {product.height && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Высота</p>
              <p className="text-lg">{product.height}</p>
            </div>
          )}

          {product.manufacturing_time && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Время производства</p>
              <p className="text-lg">{product.manufacturing_time}</p>
            </div>
          )}

          {product.variants && product.variants.length > 0 && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-2">Доступные размеры</p>
              <div className="space-y-2">
                {product.variants.map((variant) => (
                  <div key={variant.id ?? variant.size} className="flex justify-between text-lg">
                    <span>{variant.size}</span>
                    <PriceFormatter variant="inline" price={variant.price} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {product.addons && product.addons.length > 0 && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-2">Дополнительные опции</p>
              <ul className="space-y-2 text-lg">
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
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-2">Состав</p>
              <ul className="space-y-1 text-lg">
                {product.composition.map((item) => (
                  <li key={item.id}>
                    {item.name} — {item.quantity} шт.
                  </li>
                ))}
              </ul>
            </div>
          )}

          {product.pickup_locations && product.pickup_locations.length > 0 && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-2">Пункты самовывоза</p>
              <ul className="space-y-1 text-lg">
                {product.pickup_locations.map((location, index) => (
                  <li key={`${location}-${index}`}>{location}</li>
                ))}
              </ul>
            </div>
          )}

          {product.frequently_bought && product.frequently_bought.length > 0 && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-2">Часто покупают вместе</p>
              <ul className="space-y-2 text-lg">
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
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Цвета</p>
              <p className="text-lg">{product.colors.join(', ')}</p>
            </div>
          )}

          {product.created_at && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Дата создания</p>
              <p className="text-lg">
                {new Date(product.created_at).toLocaleString('ru-RU')}
              </p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/products/${product.id}/edit`)}
            className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-medium"
          >
            Редактировать
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;
