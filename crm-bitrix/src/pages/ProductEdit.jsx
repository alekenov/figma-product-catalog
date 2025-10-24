import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productsAPI } from '../services';
import { useToast } from '../components/ToastProvider';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowLeft } from 'lucide-react';

export function ProductEdit() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { showError, showSuccess } = useToast();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    description: '',
    manufacturingTime: '',
    width: '',
    height: ''
  });

  useEffect(() => {
    loadProduct();
  }, [productId]);

  async function loadProduct() {
    try {
      setLoading(true);
      const data = await productsAPI.getProduct(productId);
      setProduct(data);

      // Initialize form data
      setFormData({
        name: data.name || '',
        price: data.price || '', // Already in tenge from adapter
        description: data.description || '',
        manufacturingTime: data.manufacturing_time || '',
        width: data.width || '',
        height: data.height || ''
      });

    } catch (err) {
      const message = err.message || 'Ошибка при загрузке товара';
      showError(message);
      setTimeout(() => navigate('/products'), 2000);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    try {
      setSaving(true);

      await productsAPI.updateProduct(productId, {
        name: formData.name,
        price: parseInt(formData.price) || 0,
        description: formData.description,
        manufacturing_time: parseInt(formData.manufacturingTime) || null,
        width: parseInt(formData.width) || null,
        height: parseInt(formData.height) || null
      });

      showSuccess('Товар успешно обновлен');
      setTimeout(() => navigate(`/products/${productId}`), 1000);
    } catch (err) {
      showError(err.message || 'Ошибка при сохранении товара');
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <LoadingSpinner message="Загрузка товара..." />;

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-lg font-semibold text-red-600 mb-2">Ошибка</h2>
          <p className="text-gray-700 mb-4">Товар не найден</p>
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
            onClick={() => navigate(`/products/${productId}`)}
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            Редактировать товар
          </h1>
        </div>

        {/* Product Info */}
        <div className="bg-white rounded-lg p-6 mb-6 space-y-4">
          <div>
            <label className="block text-sm text-gray-500 mb-1">Название</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              placeholder="Название товара"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-500 mb-1">Цена (₸)</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              placeholder="10000"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-500 mb-1">Описание</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
              placeholder="Описание товара"
              rows="4"
            />
          </div>
        </div>

        {/* Characteristics */}
        <div className="bg-white rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Характеристики</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-500 mb-1">Время изготовления (мин)</label>
              <input
                type="number"
                value={formData.manufacturingTime}
                onChange={(e) => setFormData({ ...formData, manufacturingTime: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                placeholder="30"
                min="0"
              />
            </div>

            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm text-gray-500 mb-1">Ширина (см)</label>
                <input
                  type="number"
                  value={formData.width}
                  onChange={(e) => setFormData({ ...formData, width: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                  placeholder="40"
                  min="0"
                />
              </div>

              <div className="flex-1">
                <label className="block text-sm text-gray-500 mb-1">Высота (см)</label>
                <input
                  type="number"
                  value={formData.height}
                  onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                  placeholder="50"
                  min="0"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/products/${productId}`)}
            className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition font-medium"
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductEdit;
