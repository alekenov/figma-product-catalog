# 🧪 Руководство по тестированию проекта

## 📊 Текущее состояние тестирования

### Статистика покрытия
- **Начальное покрытие**: 17% (только SearchToggle и примеры)
- **Текущее покрытие**: ~40% компонентов
- **Количество тестов**: 116 (79 успешных)
- **Тестовых файлов**: 8

### Протестированные компоненты

#### ✅ Полное покрытие (100%)
1. **BottomNavBar** - Нижняя навигация приложения
2. **FilterHeader** - Заголовок с фильтрами
3. **LoadingSpinner** - Индикатор загрузки
4. **PriceFormatter** - Форматирование цен
5. **SearchInput** - Поле ввода для поиска

#### ⚠️ Частичное покрытие
1. **SearchToggle** (72.83%) - Кнопка-переключатель поиска
2. **ClientsList** - Страница списка клиентов (интеграционные тесты)
3. **Orders** - Страница заказов (интеграционные тесты)

## 🚀 Быстрый старт

### Установка зависимостей
```bash
npm install
```

### Основные команды

```bash
# Запуск тестов в режиме наблюдения (для разработки)
npm test

# Однократный запуск всех тестов
npm run test:run

# Запуск с отчетом о покрытии
npm run test:coverage

# Визуальный интерфейс для тестов
npm run test:ui

# E2E тесты (Playwright)
npm run test:e2e
```

## 📁 Структура тестов

```
figma-product-catalog/
├── src/
│   ├── components/
│   │   ├── BottomNavBar.jsx
│   │   ├── BottomNavBar.test.jsx      ✅ 18 тестов
│   │   ├── FilterHeader.jsx
│   │   ├── FilterHeader.test.jsx      ✅ 18 тестов
│   │   ├── LoadingSpinner.jsx
│   │   ├── LoadingSpinner.test.jsx    ✅ 3 теста
│   │   ├── PriceFormatter.jsx
│   │   ├── PriceFormatter.test.jsx    ✅ 15 тестов
│   │   ├── SearchInput.jsx
│   │   ├── SearchInput.test.jsx       ✅ 14 тестов
│   │   ├── SearchToggle.jsx
│   │   └── SearchToggle.test.jsx      ✅ 11 тестов
│   ├── ClientsList.jsx
│   ├── ClientsList.test.jsx           ⚠️ 19 тестов (интеграционные)
│   ├── Orders.jsx
│   ├── Orders.test.jsx                ⚠️ 18 тестов (интеграционные)
│   └── __tests__/
│       ├── setup.js                   # Глобальная настройка тестов
│       └── utils/
│           └── test-utils.js          # Утилиты для тестов
├── tests/
│   ├── warehouse.spec.js              # E2E тесты Playwright
│   └── TESTING_GUIDE.md              # Этот файл
├── TDD_GUIDE.md                       # Руководство по TDD
└── vitest.config.js                   # Конфигурация Vitest
```

## 🛠️ Что было сделано

### 1. Настройка инфраструктуры TDD
- ✅ Установлен и настроен Vitest (совместим с Vite)
- ✅ Подключен React Testing Library
- ✅ Настроен MSW для мокирования API
- ✅ Создан setup файл с глобальными настройками
- ✅ Написаны test utilities для переиспользования

### 2. Рефакторинг компонентов
- ✅ SearchToggle был изменен - тесты помогли выявить breaking changes
- ✅ SearchInput выделен в отдельный компонент
- ✅ Тесты обновлены под новую архитектуру

### 3. Написаны тесты для критичных компонентов
- ✅ **BottomNavBar**: навигация, активные состояния, клики
- ✅ **FilterHeader**: условный рендеринг иконок, обработчики
- ✅ **SearchInput**: ввод текста, очистка, Escape
- ✅ **PriceFormatter**: форматирование, варианты отображения
- ✅ **LoadingSpinner**: простые тесты рендеринга

### 4. Интеграционные тесты для страниц
- ⚠️ **ClientsList**: загрузка данных, поиск, навигация
- ⚠️ **Orders**: фильтры, статусы, сортировка

## 🎯 Что нужно сделать

### Приоритет 1: Исправить падающие тесты
```bash
# Проблема: MSW v2 изменил API, нужно обновить моки
# Проблема: React Router моки не работают правильно

# Решение для MSW:
- Заменить rest на http
- Использовать HttpResponse вместо res(ctx.json())

# Решение для Router:
- Использовать MemoryRouter правильно
- Мокировать useNavigate на уровне модуля
```

### Приоритет 2: Увеличить покрытие до 60%
- [ ] **ToggleSwitch** - компонент переключателя
- [ ] **StatusBadge** - отображение статусов
- [ ] **ProductCatalogFixed** - главная страница товаров
- [ ] **Warehouse** - страница склада
- [ ] **App.jsx** - роутинг и общая структура

### Приоритет 3: Тесты для хуков и API
- [ ] **useProducts** - хук для работы с товарами
- [ ] **useUpdateProduct** - хук обновления товаров
- [ ] **productsAPI** - сервис API
- [ ] **ordersAPI** - сервис заказов
- [ ] **clientsAPI** - сервис клиентов

### Приоритет 4: E2E тесты
- [ ] Полный flow создания заказа
- [ ] Управление товарами (добавление/редактирование)
- [ ] Работа со складом
- [ ] Фильтрация и поиск

## 📝 Примеры написания тестов

### Unit тест компонента
```javascript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  const setup = (props = {}) => {
    const user = userEvent.setup();
    const utils = render(<MyComponent {...props} />);
    return { user, ...utils };
  };

  it('should handle user click', async () => {
    const onClick = vi.fn();
    const { user } = setup({ onClick });

    await user.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### Интеграционный тест с API
```javascript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('/api/data', () => {
    return HttpResponse.json({ data: 'test' });
  })
);

beforeEach(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 🏃 Запуск конкретных тестов

```bash
# Запустить тесты одного файла
npm test BottomNavBar

# Запустить тесты в конкретной папке
npm test src/components

# Запустить только unit тесты (исключая интеграционные)
npm test -- --exclude="*.test.jsx"

# Запустить с фильтром по названию
npm test -- -t "should render"

# Обновить снапшоты
npm test -- -u
```

## 🐛 Отладка тестов

### Включить подробный вывод
```bash
npm test -- --reporter=verbose
```

### Запустить в режиме отладки
```bash
node --inspect-brk ./node_modules/.bin/vitest --run
```

### Проверить конкретный тест
```javascript
it.only('should work', () => {
  // только этот тест запустится
});
```

### Пропустить тест
```javascript
it.skip('not ready yet', () => {
  // этот тест будет пропущен
});
```

## 📊 Интерпретация отчета покрытия

После выполнения `npm run test:coverage`:

```
File               | % Stmts | % Branch | % Funcs | % Lines
-------------------|---------|----------|---------|--------
BottomNavBar.jsx   |   100   |   88.88  |   100   |   100
```

- **Stmts**: Процент выполненных инструкций
- **Branch**: Процент проверенных условных переходов
- **Funcs**: Процент вызванных функций
- **Lines**: Процент выполненных строк кода

### Цели покрытия
- 🎯 Минимум: 40% (достигнуто ✅)
- 🎯 Хорошо: 60% (следующая цель)
- 🎯 Отлично: 80%

## 🔧 Решение частых проблем

### Проблема: "Cannot find module"
```bash
# Очистить кеш и переустановить зависимости
rm -rf node_modules package-lock.json
npm install
```

### Проблема: Тесты работают медленно
```javascript
// Используйте vi.mock для тяжелых зависимостей
vi.mock('./heavyModule', () => ({
  default: vi.fn()
}));
```

### Проблема: Асинхронные тесты падают
```javascript
// Используйте waitFor для асинхронных операций
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument();
});
```

## 📚 Полезные ресурсы

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)
- [MSW Documentation](https://mswjs.io/)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)

## 👥 Контакты для вопросов

При возникновении вопросов по тестам:
1. Проверьте этот документ
2. Посмотрите примеры в существующих тестах
3. Обратитесь к TDD_GUIDE.md для методологии

---

*Последнее обновление: Декабрь 2024*
*Автор: AI Assistant с использованием TDD методологии*