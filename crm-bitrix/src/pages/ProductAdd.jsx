import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsAPI } from '../services';
import { useToast } from '../components/ToastProvider';
import { PhotoUploadBlock } from '../components/PhotoUploadBlock';
import { VideoUploadBlock } from '../components/VideoUploadBlock';
import { CollapsibleSection } from '../components/CollapsibleSection';
import { CompositionSection } from '../components/CompositionSection';
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
    photos: [],
    video: null,
    type: 'vitrina',
    name: '',
    price: '',
    manufacturingTime: '',
    composition: [],
    colors: [],
    width: '',
    height: '',
    shelfLife: '',
    description: '',
    recipient: '',
    occasions: [],
    cities: [],
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
        composition: formData.composition,
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

  const Separator = () => (
    <div className="h-px bg-gray-200 my-4" />
  );

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-md mx-auto p-4 pb-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8 pt-2">
          <button
            onClick={() => navigate('/products')}
            className="p-2 -ml-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft size={20} className="text-gray-800" />
          </button>
          <h1 className="text-2xl font-bold text-black" style={{ fontFamily: 'Open Sans' }}>
            Новый товар
          </h1>
        </div>

        {/* Section 1: Photo Upload */}
        <div className="bg-gray-100 rounded p-4 mb-4">
          <PhotoUploadBlock
            photos={formData.photos}
            onChange={(photos) => setFormData({ ...formData, photos })}
            disabled={saving}
          />
        </div>

        {/* Section 2: Video Upload */}
        <div className="bg-gray-100 rounded p-4 mb-4">
          <VideoUploadBlock
            video={formData.video}
            onChange={(video) => setFormData({ ...formData, video })}
            disabled={saving}
          />
        </div>

        <Separator />

        {/* Section 3: Category/Type */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <p className="text-sm text-gray-600">Категория</p>
            <button
              onClick={() => {}}
              className="text-sm font-medium text-purple-600 hover:text-purple-700"
            >
              Изменить
            </button>
          </div>
          <select
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            disabled={saving}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
          >
            <option value="vitrina">Сборный букет/Букеты</option>
            <option value="catalog">Каталог</option>
          </select>
        </div>

        <Separator />

        {/* Section 4: Name */}
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-2">Название товара</p>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            disabled={saving}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
            placeholder="Название"
            maxLength="100"
          />
        </div>

        <Separator />

        {/* Section 5: Price */}
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-2">Стоимость товара, ₸</p>
          <input
            type="text"
            inputMode="numeric"
            value={formData.price}
            onChange={(e) =>
              setFormData({ ...formData, price: formatPrice(e.target.value) })
            }
            disabled={saving}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
            placeholder="Цена"
          />
        </div>

        <Separator />

        {/* Section 6: Manufacturing Time */}
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-2">Время изготовления</p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              inputMode="numeric"
              value={formData.manufacturingTime}
              onChange={(e) => handleNumericInput('manufacturingTime', e.target.value)}
              disabled={saving}
              className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
              placeholder="30"
              maxLength="3"
            />
            <span className="text-sm text-black">Мин</span>
          </div>
        </div>

        <Separator />

        {/* Section 7: Composition */}
        <div className="mb-6 bg-white rounded p-4 border border-gray-200">
          <CompositionSection
            items={formData.composition}
            onChange={(composition) => setFormData({ ...formData, composition })}
            disabled={saving}
          />
        </div>

        <Separator />

        {/* Section 8: Characteristics (Collapsible) */}
        <div className="mb-6">
          <CollapsibleSection title="Характеристики" defaultOpen={true}>
            <div className="space-y-4">
              {/* Colors */}
              <div>
                <ColorSelector
                  selectedColors={formData.colors}
                  onChange={(colors) => setFormData({ ...formData, colors })}
                />
              </div>

              <div className="h-px bg-gray-200" />

              {/* Width and Height */}
              <div className="flex gap-4">
                <div className="flex-1">
                  <p className="text-sm text-gray-600 mb-2">Ширина, см</p>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={formData.width}
                    onChange={(e) => handleNumericInput('width', e.target.value)}
                    disabled={saving}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
                    placeholder="40"
                    maxLength="3"
                  />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-600 mb-2">Высота, см</p>
                  <input
                    type="text"
                    inputMode="numeric"
                    value={formData.height}
                    onChange={(e) => handleNumericInput('height', e.target.value)}
                    disabled={saving}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
                    placeholder="50"
                    maxLength="3"
                  />
                </div>
              </div>

              <div className="h-px bg-gray-200" />

              {/* Shelf Life */}
              <div>
                <p className="text-sm text-gray-600 mb-2">Сколько простоит</p>
                <input
                  type="text"
                  inputMode="numeric"
                  value={formData.shelfLife}
                  onChange={(e) => handleNumericInput('shelfLife', e.target.value)}
                  disabled={saving}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600"
                  placeholder="7"
                  maxLength="2"
                />
              </div>
            </div>
          </CollapsibleSection>
        </div>

        {/* Section 9: Additional Info (Collapsible) */}
        <div className="mb-6">
          <CollapsibleSection title="Дополнительная информация" defaultOpen={true}>
            <div className="space-y-4">
              {/* Description */}
              <div>
                <p className="text-sm text-gray-600 mb-2">Описание товара</p>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  disabled={saving}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-purple-600 resize-none"
                  placeholder="Описание"
                  rows="3"
                  maxLength="500"
                />
              </div>

              <div className="h-px bg-gray-200" />

              {/* Recipient */}
              <div>
                <RecipientSelector
                  selectedRecipient={formData.recipient}
                  onChange={(recipient) => setFormData({ ...formData, recipient })}
                />
              </div>

              <div className="h-px bg-gray-200" />

              {/* Occasions */}
              <div>
                <OccasionSelector
                  selectedOccasions={formData.occasions}
                  onChange={(occasions) => setFormData({ ...formData, occasions })}
                />
              </div>

              <div className="h-px bg-gray-200" />

              {/* Cities */}
              <div>
                <CitySelector
                  selectedCities={formData.cities}
                  onChange={(cities) => setFormData({ ...formData, cities })}
                />
              </div>
            </div>
          </CollapsibleSection>
        </div>

        <Separator />

        {/* Action Button */}
        <button
          onClick={handleSave}
          disabled={
            saving ||
            !formData.name ||
            !formData.price ||
            formData.photos.length === 0
          }
          className="w-full h-12 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded font-medium transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          style={{ height: '46px' }}
        >
          {saving ? 'Опубликование...' : 'Опубликовать'}
        </button>
      </div>
    </div>
  );
}

export default ProductAdd;
