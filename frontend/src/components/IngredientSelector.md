# IngredientSelector Component

## Назначение
Кастомный селектор ингредиентов с поиском, заменяющий стандартный `<select>` для улучшенного UX при выборе складских позиций в рецептуре товаров.

## Преимущества над стандартным select

### Старый подход (select):
```jsx
<option value="1">Роза розовая (остаток: 150 шт, 50000 ₸/шт)</option>
```
❌ Перегруженный текст в каждой опции
❌ Трудно сканировать глазами при 12+ позициях
❌ Нет возможности поиска
❌ Плохая читаемость на мобильных устройствах

### Новый подход (IngredientSelector):
✅ Поиск по названию в реальном времени
✅ Визуальное разделение информации (название + детали)
✅ Карточки с читаемой структурой
✅ Цветовая индикация низких остатков (< 10 шт)
✅ Форматированные цены (50,000 ₸ вместо 50000)
✅ Закрытие dropdown при клике вне компонента

## API

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `warehouseItems` | `Array<WarehouseItem>` | ✅ | - | Список складских позиций для выбора |
| `selectedItemId` | `number \| string` | ❌ | - | ID выбранной позиции |
| `onSelect` | `(itemId: number) => void` | ✅ | - | Callback при выборе позиции |
| `placeholder` | `string` | ❌ | "Начните вводить название..." | Placeholder для пустого поля |

### WarehouseItem Type

```typescript
interface WarehouseItem {
  id: number;
  name: string;           // Название позиции
  quantity: number;       // Остаток на складе
  cost_price: number;     // Цена за единицу
}
```

## Использование

```jsx
import IngredientSelector from './components/IngredientSelector';

const RecipeForm = () => {
  const [selectedItemId, setSelectedItemId] = useState('');
  const warehouseItems = [
    { id: 1, name: 'Роза розовая', quantity: 150, cost_price: 50000 },
    { id: 2, name: 'Пион розовый', quantity: 80, cost_price: 80000 }
  ];

  return (
    <IngredientSelector
      warehouseItems={warehouseItems}
      selectedItemId={selectedItemId}
      onSelect={(itemId) => setSelectedItemId(itemId)}
      placeholder="Начните вводить название..."
    />
  );
};
```

## Визуальные состояния

### Пустое состояние
- Показывается placeholder
- Иконка поиска справа

### Выбрано значение
- Показывается название выбранной позиции
- Зеленая галочка справа
- При клике открывается dropdown с полным списком

### Поиск активен
- Dropdown открыт
- Фильтруется список по вводимому тексту
- Case-insensitive поиск по названию

### Карточка элемента
```
┌─────────────────────────────────┐
│ Роза розовая              (название) │
│ Остаток: 150 шт  Цена: 50,000 ₸/шт │
└─────────────────────────────────┘
```

### Низкий остаток (< 10 шт)
- Количество показывается красным цветом
- Предупреждающий индикатор

## Интеграция в существующие компоненты

### EditProduct.jsx
Заменен старый select на IngredientSelector в разделе "Состав букета" (строка 303-308)

### AddProduct.jsx
Заменен старый select на IngredientSelector в разделе "Состав букета" (строка 323-328)

## Дизайн-токены

Используются стандартные токены из Tailwind конфига:
- `gray-border` - границы
- `gray-disabled` - вторичный текст
- `gray-placeholder` - placeholder
- `gray-input` - фон карточек
- `gray-input-alt` - выбранная карточка
- `green-success` - галочка выбора

## UX паттерны

1. **Click outside to close**: Dropdown закрывается при клике вне компонента
2. **Search clear on select**: Поисковый запрос очищается после выбора
3. **Visual feedback**: Hover эффекты на карточках
4. **Keyboard friendly**: Можно сразу начинать печатать после фокуса

## Производительность

- **Фильтрация**: O(n) с использованием `.filter()` и `.includes()`
- **Рендеринг**: Оптимизирован для 50+ позиций
- **Event listeners**: Автоматическая очистка при unmount

## Будущие улучшения

- [ ] Keyboard navigation (Arrow Up/Down, Enter, Escape)
- [ ] Highlight совпадений в результатах поиска
- [ ] Виртуализация для 100+ позиций
- [ ] Сортировка (по названию, остатку, цене)
- [ ] Фильтры (минимальный остаток, ценовой диапазон)
