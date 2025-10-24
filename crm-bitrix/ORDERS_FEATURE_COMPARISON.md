# Сравнение функционала: Bitrix CRM ↔ Новый Frontend

**Дата анализа:** 2025-10-24
**Bitrix компонент:** `/local/components/crm/order.list.new/class.php` (1700 строк)
**Новый фронтенд:** `/frontend/src/` (модульная архитектура)

---

## 📊 СПИСОК ЗАКАЗОВ (Orders List)

### ✅ Реализовано в новом фронтенде

| Функция | Bitrix | Новый Frontend | Файл |
|---------|--------|----------------|------|
| Список заказов с пагинацией | ✅ | ✅ | `Orders.jsx` |
| Поиск по имени/телефону/номеру | ✅ | ✅ | `Orders.jsx:72-76` |
| Фильтр "Мои заказы" | ✅ | ✅ | `Orders.jsx:14,33` |
| Отображение статуса заказа | ✅ | ✅ | `Orders.jsx:50-69` |
| Клик на заказ → детали | ✅ | ✅ | `Orders.jsx:197` |
| Подсчет позиций в заказе | ✅ | ✅ | `Orders.jsx:230` |
| Превью товаров в заказе | ✅ | ✅ | `Orders.jsx:236-245` |

### ❌ НЕ реализовано (нужно добавить)

| Функция | Bitrix метод | Приоритет | Описание |
|---------|--------------|-----------|----------|
| **Фильтр по статусу** | `getOrdersAction` filter.statusId | 🔴 ВЫСОКИЙ | Фильтровать: Новые, Оплачен, Собран, В доставке и т.д. |
| **Фильтр по дате доставки** | `getOrdersAction` filter.deliveryDate | 🔴 ВЫСОКИЙ | Диапазон дат (от-до) для доставки |
| **Фильтр по типу заказа** | `getOrdersAction` filter.orderType | 🟡 СРЕДНИЙ | opt, pickup, packs, noPickup |
| **Фильтр по городу** | `getOrdersAction` filter.deliveryId | 🟡 СРЕДНИЙ | Алматы, Астана и т.д. |
| **Архивные заказы** | `getOrdersAction` filter.statusId='ARCHIVE' | 🟡 СРЕДНИЙ | Отдельная вкладка для старых заказов |
| **Сортировка по дате** | `getOrdersAction` sort='asc'/'desc' | 🟢 НИЗКИЙ | По возрастанию/убыванию даты доставки |
| **Календарь выбора даты** | UI элемент | 🟡 СРЕДНИЙ | Иконка календаря есть (Orders.jsx:109), но функционал не подключен |
| **Общее кол-во заказов по статусу** | `getTotalOrdersAction` | 🟢 НИЗКИЙ | Показать badges с количеством (Новые: 5, Оплачено: 12) |

---

## 📝 ДЕТАЛИ ЗАКАЗА (Order Detail)

### ✅ Реализовано в новом фронтенде

| Функция | Bitrix | Новый Frontend | Файл |
|---------|--------|----------------|------|
| Просмотр деталей заказа | ✅ | ✅ | `OrderDetail.jsx` |
| История изменений | ✅ | ✅ | `OrderDetail.jsx:100-117` |
| Изменение статуса | ✅ | ✅ | `OrderDetail.jsx:70-98` |
| Редактирование адреса/даты/заметок | ✅ | ✅ | `OrderDetail.jsx:324-445` |
| Назначение ответственного | ✅ | ✅ | `OrderDetail.jsx:172-212` |
| Назначение курьера | ✅ | ✅ | `OrderDetail.jsx:214-255` |
| Загрузка фото до доставки | ✅ | ✅ | `OrderDetail.jsx:448-492` |
| Удаление фото | ✅ | ✅ | `OrderDetail.jsx:494-516` |
| Копирование ссылки для клиента | ✅ | ✅ | `OrderDetail.jsx:573-589` |
| Kaspi возврат средств | ✅ | ✅ | `OrderDetail.jsx:592-649` |
| Отмена заказа | ✅ | ✅ | `OrderDetail.jsx:316-322` |
| Отображение данных получателя | ✅ | ✅ | `OrderDetail.jsx:884-894` |
| Отображение данных заказчика | ✅ | ✅ | `OrderDetail.jsx:896-905` |
| WhatsApp иконки для связи | ✅ | ✅ | `OrderDetail.jsx:889-891` |

### ❌ НЕ реализовано (нужно добавить)

| Функция | Bitrix метод | Приоритет | Описание |
|---------|--------------|-----------|----------|
| **Заметки к заказу** | `addNoteAction`, `removeNoteAction` | 🔴 ВЫСОКИЙ | Добавление/удаление заметок флориста (сейчас только в notes) |
| **Проблемный заказ** | `problemOrderAction(id, reason)` | 🔴 ВЫСОКИЙ | Пометить заказ как проблемный с указанием причины |
| **Доплата за заказ** | `surchargePayOrderAction(id, phone, value, message, namePayment)` | 🟡 СРЕДНИЙ | Запросить доплату через Kaspi Pay |
| **Частичный возврат** | `returnPayOrderAction(id, text, false, amount)` | ✅ Реализовано | В Kaspi refund есть (OrderDetail.jsx:618-628) |
| **Аукцион (без ответственного)** | `getDetailOrderAction` isAuction | 🟡 СРЕДНИЙ | Если нет responsibleId → показать badge "Аукцион" |
| **SMS "Узнать адрес у получателя"** | `sendSmsClarifyAddressAction(orderId)` | 🟢 НИЗКИЙ | Если askAddress=true и не отправлено → показать кнопку |
| **Отправить курьеру в Telegram** | `sendOrderCourierTeleramAction(orderId)` | 🟢 НИЗКИЙ | Уведомить курьера о назначении |
| **Yandex/Indrive доставка** | `createYandexOrderAction`, `cancelYandexOrderAction` | 🟢 НИЗКИЙ | Интеграция с Yandex Delivery (было в Bitrix) |
| **Информация о курьере (трекинг)** | `getDetailOrderAction` yandexDelivery.courier | 🟢 НИЗКИЙ | Показать координаты курьера на карте |
| **Данные partner (если заказ от партнера)** | `getDetailOrderAction` partnerName | 🟢 НИЗКИЙ | Показать имя партнера если responsibleId - партнер |
| **Write-off products (списанные товары)** | `getDetailOrderAction` writeOffProducts | 🟡 СРЕДНИЙ | Список товаров списанных со склада для этого заказа |
| **Разрешения на просмотр данных** | `canViewOrderCustomersInfo` | 🟢 НИЗКИЙ | Скрыть телефоны получателя если нет прав |
| **Клиент-рейтинг букета (feedback)** | ✅ Реализовано | Отображение лайка/дизлайка клиента (OrderDetail.jsx:769-787) |

---

## ➕ СОЗДАНИЕ/РЕДАКТИРОВАНИЕ ЗАКАЗА

### ✅ Реализовано в новом фронтенде

| Функция | Bitrix | Новый Frontend | Файл |
|---------|--------|----------------|------|
| Форма создания заказа | ✅ | ✅ | `CreateOrder.jsx` / `CreateOrderCustomer.jsx` |
| Редактирование данных заказа | ✅ | ✅ | `OrderDetail.jsx:324-445` |

### ❌ НЕ реализовано (нужно добавить)

| Функция | Bitrix метод | Приоритет | Описание |
|---------|--------------|-----------|----------|
| **Создание заказа (полная форма)** | `createOrderAction` | 🔴 ВЫСОКИЙ | Полная форма со всеми полями из Bitrix |
| **Поиск товаров при создании** | `searchProductsAction(phrase, cityId)` | 🔴 ВЫСОКИЙ | Автодополнение при вводе названия товара |
| **Подарки (gifts)** | `createOrderAction` gifts | 🟡 СРЕДНИЙ | Добавление подарочных товаров |
| **Открытка (postCard)** | `createOrderAction` postCard | 🟡 СРЕДНИЙ | Текст открытки к заказу |
| **Анонимный отправитель** | `editOrderNewAction` anonimSender | 🟡 СРЕДНИЙ | Флаг "Не называть имя отправителя" |
| **Не звонить получателю (isSurprise)** | `createOrderAction` dontCallReciever | 🟡 СРЕДНИЙ | Флаг сюрприза |
| **Выбор системы оплаты** | `createOrderAction` paySystemId | 🟡 СРЕДНИЙ | Kaspi / Наличные / Карта и т.д. |
| **Детализация адреса** | `editOrderNewAction` street, apartment, entrance, floor | 🟢 НИЗКИЙ | Раздельные поля вместо одной строки |

---

## 📦 СПЕЦИАЛЬНЫЕ ФУНКЦИИ

### ❌ Еще НЕ реализовано

| Функция | Bitrix метод | Приоритет | Описание |
|---------|--------------|-----------|----------|
| **Принять заказ (acceptOrder)** | `acceptOrderAction(orderId)` | 🟡 СРЕДНИЙ | Изменить статус на "Принят" + доп. логика |
| **Завершить заказ** | `finishOrderAction(orderId)` | 🟡 СРЕДНИЙ | Статус "Доставлен" + доп. действия |
| **Установить "Оплачен"** | `setPayedAction(orderId)` | 🟡 СРЕДНИЙ | Установить статус оплаты |
| **Доставлен** | `setDeliveredAction()` | 🟡 СРЕДНИЙ | Bulk action для завершения доставки |
| **Отправить курьеру** | `sendToCourierAction(orderId, approximateDelivery)` | 🟡 СРЕДНИЙ | Указать примерное время доставки |
| **Отмена Yandex доставки** | `cancelYandexOrderAction(orderId)` | 🟢 НИЗКИЙ | Если была интеграция с Yandex |
| **Получить стоимость доставки** | `getOrderDeliveryPriceAction(params)` | 🟢 НИЗКИЙ | Калькулятор стоимости |

---

## 🎯 РЕКОМЕНДАЦИИ ПО ВНЕДРЕНИЮ

### 1. ВЫСОКИЙ ПРИОРИТЕТ (сделать в первую очередь)

#### **Фильтры для списка заказов** (`Orders.jsx`)

**Цель:** Позволить флористам быстро находить заказы

**Реализация:**
```jsx
// Добавить в Orders.jsx
const [filters, setFilters] = useState({
  status: '', // 'new', 'paid', 'accepted', 'assembled', 'in_delivery', 'delivered', 'cancelled'
  deliveryDate: { from: '', to: '' },
  orderType: '', // 'opt', 'pickup', 'packs', 'noPickup'
  cityId: ''
});

// Обновить fetchOrders
const params = {
  limit: 50,
  ...(myOrdersFilter && { assigned_to_me: true }),
  ...(filters.status && { status: filters.status }),
  ...(filters.deliveryDate.from && { delivery_from: filters.deliveryDate.from }),
  ...(filters.deliveryDate.to && { delivery_to: filters.deliveryDate.to }),
  ...(filters.orderType && { order_type: filters.orderType }),
  ...(filters.cityId && { city_id: filters.cityId })
};
```

**UI:**
- Создать компонент `OrderFiltersPanel.jsx`
- Добавить кнопки-чипы для быстрых фильтров (Сегодня, Завтра, Эта неделя)
- Dropdown для выбора статуса
- Date range picker для диапазона дат

---

#### **Заметки к заказу** (`OrderDetail.jsx`)

**Цель:** Флористы оставляют комментарии по ходу работы

**Реализация:**
```jsx
// Добавить в OrderDetail.jsx секцию "Заметки флориста"
const [notes, setNotes] = useState([]);
const [newNote, setNewNote] = useState('');

const handleAddNote = async () => {
  await ordersAPI.addNote(orderId, newNote);
  fetchNotes();
  setNewNote('');
};

const handleDeleteNote = async (noteId) => {
  await ordersAPI.removeNote(orderId, noteId);
  fetchNotes();
};
```

**Backend API:**
```python
# backend/api/orders/__init__.py
@router.post("/{order_id}/notes")
async def add_order_note(order_id: int, note_text: str, current_user: User = Depends(get_current_user)):
    # Создать запись в таблице OrderNotes
    pass

@router.delete("/{order_id}/notes/{note_id}")
async def remove_order_note(order_id: int, note_id: int, current_user: User = Depends(get_current_user)):
    # Удалить запись
    pass
```

---

#### **Проблемный заказ** (`OrderDetail.jsx`)

**Цель:** Помечать заказы с проблемами для эскалации

**Реализация:**
```jsx
// Добавить в OrderDetail.jsx кнопку "Проблема"
const [isProblem, setIsProblem] = useState(false);
const [problemReason, setProblemReason] = useState('');

const handleMarkProblem = async () => {
  await ordersAPI.markProblem(orderId, problemReason);
  showSuccess('Заказ помечен как проблемный');
};
```

**UI:**
- Красная кнопка "⚠️ Проблема" в секции действий
- Modal с textarea для описания проблемы
- Badge "Проблемный заказ" в списке заказов

---

### 2. СРЕДНИЙ ПРИОРИТЕТ

#### **Доплата за заказ** (`OrderDetail.jsx`)

**Цель:** Запросить доп. оплату через Kaspi Pay (например, за доставку или изменение букета)

**Реализация:**
```jsx
// Аналогично Kaspi refund, но метод surcharge
const handleKaspiSurcharge = async () => {
  await fetch('http://localhost:8014/api/v1/kaspi/surcharge', {
    method: 'POST',
    body: JSON.stringify({
      order_id: orderId,
      phone: orderData.phone,
      amount: surchargeAmount,
      message: surchargeReason,
      payment_name: 'Доплата за заказ'
    })
  });
};
```

---

#### **Аукцион заказов** (`Orders.jsx`, `OrderDetail.jsx`)

**Цель:** Показать заказы без ответственного как "Аукцион" для захвата флористами

**Реализация:**
```jsx
// В OrderDetail.jsx
{!orderData.assigned_to_id && (
  <div className="bg-yellow-100 border border-yellow-400 rounded p-3 mb-4">
    <div className="flex items-center gap-2">
      <span className="text-xl">🔨</span>
      <div>
        <div className="font-bold">Аукцион</div>
        <div className="text-sm">Никто еще не взял этот заказ</div>
      </div>
    </div>
    <button
      onClick={handleTakeOrder}
      className="mt-2 w-full bg-yellow-500 text-white rounded py-2"
    >
      Взять заказ себе
    </button>
  </div>
)}
```

---

### 3. НИЗКИЙ ПРИОРИТЕТ

- **Yandex/Indrive доставка** - Если планируется интеграция
- **Отправка в Telegram** - Уже есть в backend через MCP, можно просто добавить кнопку
- **Партнеры** - Если используется система партнеров
- **SMS уведомления** - Автоматизация через backend

---

## 📋 ИТОГОВАЯ ТАБЕЛЬ ОТЛИЧИЙ

| Категория | Функций в Bitrix | Реализовано в новом | Недостает |
|-----------|------------------|---------------------|-----------|
| **Список заказов** | 9 | 7 | 2 (фильтры, сортировки) |
| **Детали заказа** | 22 | 13 | 9 (заметки, проблемы, доплаты) |
| **Создание/редактирование** | 10 | 2 | 8 (полная форма) |
| **Специальные функции** | 8 | 0 | 8 (принять, завершить, доставка) |
| **ИТОГО** | **49** | **22** | **27** |

**Процент готовности:** ~45%

---

## 🛠 ПЛАН ДЕЙСТВИЙ

### Этап 1: Критичный функционал (2-3 дня)
1. ✅ Фильтры по статусу в Orders.jsx
2. ✅ Фильтр по дате доставки
3. ✅ Заметки к заказу
4. ✅ Пометка "Проблемный заказ"

### Этап 2: Расширенный функционал (3-5 дней)
1. ✅ Доплата за заказ (Kaspi surcharge)
2. ✅ Аукцион заказов
3. ✅ Полная форма создания заказа
4. ✅ Поиск товаров при создании

### Этап 3: Дополнительный функционал (по необходимости)
1. ✅ Yandex/Indrive интеграция
2. ✅ SMS уведомления
3. ✅ Партнеры
4. ✅ Write-off products

---

## 💡 ЗАКЛЮЧЕНИЕ

Новый фронтенд уже имеет **сильную основу** с модульной архитектурой, Context API и основными функциями управления заказами.

**Главные отличия от Bitrix:**
- ✅ **Лучше:** Модульность, тесты, современный UI, Kaspi Pay интеграция
- ❌ **Хуже:** Нет фильтров, заметок, проблемных заказов, доплат

**Следующие шаги:**
1. Добавить фильтры в список заказов
2. Реализовать систему заметок
3. Добавить пометку "Проблемный заказ"
4. Доплаты через Kaspi Pay

После этого новый фронтенд будет **на уровне или лучше** старого Bitrix CRM.
