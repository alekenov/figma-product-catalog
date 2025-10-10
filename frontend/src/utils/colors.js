/**
 * Цветовые константы для букетов
 * Используется в Admin Panel и Website для единообразного отображения
 *
 * Названия сохраняются в БД для лучшего понимания ИИ/MCP сервером
 */

export const BOUQUET_COLORS = [
  {
    id: 'red',
    name: 'Красный',
    hex: '#FF4444',
    description: 'Красные розы, гвоздики'
  },
  {
    id: 'pink',
    name: 'Розовый',
    hex: '#FFB6C1',
    description: 'Розовые розы, пионы'
  },
  {
    id: 'white',
    name: 'Белый',
    hex: '#FFFFFF',
    border: true, // Нужна граница для белого цвета
    description: 'Белые розы, лилии, хризантемы'
  },
  {
    id: 'mixed',
    name: 'Микс',
    hex: 'linear-gradient(90deg, #FF4444 0%, #FFB6C1 50%, #FFD700 100%)',
    description: 'Разноцветный букет'
  },
  {
    id: 'purple',
    name: 'Фиолетовый',
    hex: '#9B59B6',
    description: 'Фиолетовые тюльпаны, ирисы'
  },
  {
    id: 'cream',
    name: 'Кремовый',
    hex: '#F5E6D3',
    border: true, // Нужна граница для светлого цвета
    description: 'Кремовые розы, эустома'
  },
  {
    id: 'yellow',
    name: 'Желтый',
    hex: '#FFD700',
    description: 'Желтые розы, подсолнухи'
  },
  {
    id: 'blue',
    name: 'Синий',
    hex: '#4A90E2',
    description: 'Синие гортензии, дельфиниумы'
  }
];

/**
 * Mapping для быстрого lookup: название → hex color
 * Используется для отображения цветных плашек по названию из БД
 */
export const COLOR_DISPLAY_MAP = BOUQUET_COLORS.reduce((acc, color) => {
  acc[color.name] = {
    hex: color.hex,
    border: color.border
  };
  return acc;
}, {});

/**
 * Получить hex цвет по названию
 * @param {string} colorName - Название цвета (например, "Красный")
 * @returns {string} - Hex код или gradient
 */
export const getColorHex = (colorName) => {
  return COLOR_DISPLAY_MAP[colorName]?.hex || '#E0E0E0';
};

/**
 * Нужна ли граница для цвета (для светлых цветов)
 * @param {string} colorName - Название цвета
 * @returns {boolean}
 */
export const needsBorder = (colorName) => {
  return COLOR_DISPLAY_MAP[colorName]?.border || false;
};
