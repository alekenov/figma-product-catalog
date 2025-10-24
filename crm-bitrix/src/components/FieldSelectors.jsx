import { X } from 'lucide-react';

// Color options for bouquets
const COLOR_OPTIONS = [
  { id: 'red', name: 'Красные', color: '#E53E3E' },
  { id: 'pink', name: 'Розовые', color: '#ED64A6' },
  { id: 'white', name: 'Белые', color: '#E8E8E8' },
  { id: 'yellow', name: 'Жёлтые', color: '#ECC94B' },
  { id: 'purple', name: 'Фиолетовые', color: '#9F7AEA' },
  { id: 'orange', name: 'Оранжевые', color: '#ED8936' },
  { id: 'peach', name: 'Персиковые', color: '#FBB6CE' },
  { id: 'cream', name: 'Кремовые', color: '#FFF5E6' },
];

// Occasion options
const OCCASION_OPTIONS = [
  { id: 'birthday', name: 'День рождения' },
  { id: 'anniversary', name: 'Годовщина' },
  { id: 'congratulations', name: 'Поздравления' },
  { id: 'love', name: 'Любовь' },
  { id: 'sympathy', name: 'Сочувствие' },
  { id: 'wedding', name: 'Свадьба' },
  { id: 'graduation', name: 'Выпускной' },
  { id: 'romance', name: 'Романтика' },
];

// City options
const CITY_OPTIONS = [
  { id: 'almaty', name: 'Алматы' },
  { id: 'astana', name: 'Астана' },
  { id: 'karaganda', name: 'Караганда' },
  { id: 'kokshetau', name: 'Кокшетау' },
];

// Recipient type options
const RECIPIENT_OPTIONS = [
  { id: 'woman', name: 'Женщине' },
  { id: 'man', name: 'Мужчине' },
  { id: 'girl', name: 'Девочке' },
  { id: 'boy', name: 'Мальчику' },
];

export function ColorSelector({ selectedColors = [], onChange }) {
  const toggleColor = (colorId) => {
    if (selectedColors.includes(colorId)) {
      onChange(selectedColors.filter((id) => id !== colorId));
    } else {
      onChange([...selectedColors, colorId]);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-900">
        Цвета букета
      </label>
      <div className="flex flex-wrap gap-2">
        {COLOR_OPTIONS.map((color) => (
          <button
            key={color.id}
            onClick={() => toggleColor(color.id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition ${
              selectedColors.includes(color.id)
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-300 bg-white hover:border-gray-400'
            }`}
          >
            <div
              className="w-4 h-4 rounded-full border border-gray-300"
              style={{ backgroundColor: color.color }}
            />
            <span className="text-sm text-gray-900">{color.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export function OccasionSelector({ selectedOccasions = [], onChange }) {
  const toggleOccasion = (occasionId) => {
    if (selectedOccasions.includes(occasionId)) {
      onChange(selectedOccasions.filter((id) => id !== occasionId));
    } else {
      onChange([...selectedOccasions, occasionId]);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-900">
        Повод
      </label>
      <div className="flex flex-wrap gap-2">
        {OCCASION_OPTIONS.map((occasion) => (
          <button
            key={occasion.id}
            onClick={() => toggleOccasion(occasion.id)}
            className={`px-3 py-1 rounded-full border text-sm transition ${
              selectedOccasions.includes(occasion.id)
                ? 'border-purple-600 bg-purple-100 text-purple-900'
                : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'
            }`}
          >
            {occasion.name}
          </button>
        ))}
      </div>
    </div>
  );
}

export function CitySelector({ selectedCities = [], onChange }) {
  const toggleCity = (cityId) => {
    if (selectedCities.includes(cityId)) {
      onChange(selectedCities.filter((id) => id !== cityId));
    } else {
      onChange([...selectedCities, cityId]);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-900">
        Доступен в городах
      </label>
      <div className="flex flex-wrap gap-2">
        {CITY_OPTIONS.map((city) => (
          <button
            key={city.id}
            onClick={() => toggleCity(city.id)}
            className={`px-3 py-1 rounded-full border text-sm transition ${
              selectedCities.includes(city.id)
                ? 'border-purple-600 bg-purple-100 text-purple-900'
                : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'
            }`}
          >
            {city.name}
          </button>
        ))}
      </div>
    </div>
  );
}

export function RecipientSelector({ selectedRecipient = '', onChange }) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-900">
        Кому
      </label>
      <select
        value={selectedRecipient}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
      >
        <option value="">Выберите получателя</option>
        {RECIPIENT_OPTIONS.map((recipient) => (
          <option key={recipient.id} value={recipient.id}>
            {recipient.name}
          </option>
        ))}
      </select>
    </div>
  );
}
