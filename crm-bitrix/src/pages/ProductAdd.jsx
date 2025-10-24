import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsAPI } from '../services';
import { useToast } from '../components/ToastProvider';
import { PhotoUploadBlock } from '../components/PhotoUploadBlock';
import { VideoUploadBlock } from '../components/VideoUploadBlock';
import { CollapsibleSection } from '../components/CollapsibleSection';
import {
  ColorSelector,
  OccasionSelector,
  CitySelector,
  RecipientSelector,
} from '../components/FieldSelectors';
import { ArrowLeft } from 'lucide-react';

export function ProductAdd() {
  const navigate = useNavigate();
  const { showError, showSuccess } = useToast();
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    // Media
    photos: [],
    video: null,
    // Main info
    type: 'vitrina',
    name: '',
    price: '',
    description: '',
    // Characteristics
    manufacturingTime: '',
    width: '',
    height: '',
    // Additional info
    shelfLife: '',
    // Metadata
    recipient: '',
    occasions: [],
    cities: [],
    colors: [],
  });

  const formatPrice = (value) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  };

  const handleNumericInput = (field, value) => {
    const numericValue = value.replace(/\D/g, '');
    setFormData({ ...formData, [field]: numericValue });
  };

  async function handleSave() {
    try {
      if (!formData.name.trim()) {
        showError('Название товара обязательно');
        return;
      }
      if (!formData.price.trim()) {
        showError('Цена товара обязательна');
        return;
      }
      if (formData.photos.length === 0) {
        showError('Загрузите минимум одно фото');
        return;
      }

      setSaving(true);

      const priceValue = parseInt(formData.price.replace(/\s/g, ''));
      const primaryPhoto = formData.photos[0];

      await productsAPI.createProduct({
        name: formData.name,
        type: formData.type,
        price: priceValue,
        image: primaryPhoto,
        description: formData.description || null,
        manufacturing_time: parseInt(formData.manufacturingTime) || null,
        width: parseInt(formData.width) || null,
        height: parseInt(formData.height) || null,
        shelfLife: parseInt(formData.shelfLife) || null,
        video: formData.video || null,
        recipient: formData.recipient || null,
        occasions: formData.occasions,
        cities: formData.cities,
        colors: formData.colors,
      });

      showSuccess('Товар успешно создан');
      setTimeout(() => navigate('/products'), 1000);
    } catch (err) {
      showError(err.message || 'Ошибка при создании товара');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto p-4 pb-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/products')}
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ArrowLeft size={24} />
          </button>
          <h1
            className="text-2xl font-bold text-gray-900"
            style={{ fontFamily: 'Open Sans' }}
          >
            Новый товар
          </h1>
        </div>

        {/* Section 1: Photo Upload */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <PhotoUploadBlock
            photos={formData.photos}
            onChange={(photos) => setFormData({ ...formData, photos })}
            disabled={saving}
          />
        </div>

        {/* Section 2: Video Upload */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <VideoUploadBlock
            video={formData.video}
            onChange={(video) => setFormData({ ...formData, video })}
            disabled={saving}
          />
        </div>

        {/* Section 3: Product Type */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Тип товара <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            disabled={saving}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
          >
            <option value="vitrina">Витрина (готовый букет)</option>
            <option value="catalog">Каталог</option>
          </select>
        </div>

        {/* Section 4: Name */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Название <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            disabled={saving}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
            placeholder="Название товара"
            maxLength="100"
          />
        </div>

        {/* Section 5: Price */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Цена <span className="text-red-500">*</span>
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              inputMode="numeric"
              value={formData.price}
              onChange={(e) =>
                setFormData({ ...formData, price: formatPrice(e.target.value) })
              }
              disabled={saving}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              placeholder="10000"
            />
            <span className="text-gray-700">₸</span>
          </div>
        </div>

        {/* Section 6: Description */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Описание
          </label>
          <textarea
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            disabled={saving}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
            placeholder="Описание товара"
            rows="4"
            maxLength="500"
          />
        </div>

        {/* Section 7: Characteristics (Collapsible) */}
        <div className="mb-4">
          <CollapsibleSection title="Характеристики">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Время изготовления (мин)
                </label>
                <input
                  type="text"
                  inputMode="numeric"
                  value={formData.manufacturingTime}
                  onChange={(e) =>
                    handleNumericInput('manufacturingTime', e.target.value)
                  }
                  disabled={saving}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                  placeholder="30"
                  maxLength="3"
                />
              </div>

              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Ширина (см)
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={formData.width}
                    onChange={(e) => handleNumericInput('width', e.target.value)}
                    disabled={saving}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                    placeholder="40"
                    maxLength="3"
                  />
                </div>

                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Высота (см)
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={formData.height}
                    onChange={(e) => handleNumericInput('height', e.target.value)}
                    disabled={saving}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                    placeholder="50"
                    maxLength="3"
                  />
                </div>
              </div>
            </div>
          </CollapsibleSection>
        </div>

        {/* Section 8: Additional Info (Collapsible) */}
        <div className="mb-4">
          <CollapsibleSection title="Дополнительная информация">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Сколько простоит (дней)
              </label>
              <input
                type="text"
                inputMode="numeric"
                value={formData.shelfLife}
                onChange={(e) => handleNumericInput('shelfLife', e.target.value)}
                disabled={saving}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                placeholder="7"
                maxLength="2"
              />
            </div>
          </CollapsibleSection>
        </div>

        {/* Section 9: Recipient Type */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <RecipientSelector
            selectedRecipient={formData.recipient}
            onChange={(recipient) => setFormData({ ...formData, recipient })}
          />
        </div>

        {/* Section 10: Occasions */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <OccasionSelector
            selectedOccasions={formData.occasions}
            onChange={(occasions) => setFormData({ ...formData, occasions })}
          />
        </div>

        {/* Section 11: Cities */}
        <div className="bg-white rounded-lg p-6 mb-4 border border-gray-200">
          <CitySelector
            selectedCities={formData.cities}
            onChange={(cities) => setFormData({ ...formData, cities })}
          />
        </div>

        {/* Section 12: Colors */}
        <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
          <ColorSelector
            selectedColors={formData.colors}
            onChange={(colors) => setFormData({ ...formData, colors })}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/products')}
            disabled={saving}
            className="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ height: '46px' }}
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            disabled={
              saving ||
              !formData.name ||
              !formData.price ||
              formData.photos.length === 0
            }
            className="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ height: '46px' }}
          >
            {saving ? 'Создание...' : 'Создать товар'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductAdd;
