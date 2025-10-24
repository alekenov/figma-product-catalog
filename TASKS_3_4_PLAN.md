# План выполнения Tasks 3-4: Profile.jsx и OrderDetail.jsx

**Дата создания**: 23 октября 2025
**Статус**: ✅ УТВЕРЖДЁН пользователем
**Подход**: Сбалансированный (Context API + Custom Hooks)

---

## 📋 TASK 3: Profile.jsx (1088 строк → 6 файлов)

### Цель
Разделить монолитный Profile.jsx на модульную структуру с Context API для избежания prop drilling.

### Новая структура
```
frontend/src/components/profile/
├── ProfileContext.jsx         (80 lines)  - Context для profile data
├── Profile.jsx                (150 lines) - Main orchestrator с табами
├── ProfileInfo.jsx            (250 lines) - User info + team management
├── ShopSettings.jsx           (350 lines) - Shop settings + working hours
└── hooks/
    └── useTeamManagement.js   (120 lines) - Team invite/edit/delete logic
```

### Текущее состояние
- **Размер**: 1,088 строк
- **useState**: 21 hooks
- **Обработчики**: 12 функций
- **Функциональность**:
  - Team management (invite, edit role, delete members)
  - Shop settings (name, address, contact info)
  - Working hours management (morning/evening)
  - Delivery settings (zones, minimum order)
  - Invitations management

### Разделение функциональности

#### ProfileContext.jsx (новый файл)
**Ответственность**: Централизованное управление состоянием профиля

**State**:
```javascript
{
  profileData: null,      // User profile info
  teamMembers: [],        // Team members list
  teamInvitations: [],    // Pending invitations
  shopSettings: null,     // Shop configuration
  loading: true,
  error: null
}
```

**Методы**:
- `refreshProfile()` - Reload user profile
- `refreshTeam()` - Reload team members & invitations
- `refreshShop()` - Reload shop settings

**Использование**:
```javascript
export const ProfileProvider = ({ children }) => {
  const [state, setState] = useState(initialState);

  const refreshProfile = async () => { /* ... */ };
  const refreshTeam = async () => { /* ... */ };
  const refreshShop = async () => { /* ... */ };

  return (
    <ProfileContext.Provider value={{ ...state, refreshProfile, refreshTeam, refreshShop }}>
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = () => useContext(ProfileContext);
```

#### Profile.jsx (главный оркестратор)
**Размер**: ~150 строк

**Ответственность**:
- Layout wrapper
- Navigation handling
- Logout functionality
- Рендер ProfileInfo и ShopSettings
- BottomNavBar

**Структура**:
```javascript
const Profile = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [activeNav, setActiveNav] = useState('profile');

  const handleNavChange = (navId, route) => { /* ... */ };
  const handleLogout = async () => { /* ... */ };

  return (
    <ProfileProvider>
      <div className="figma-container">
        {/* Header */}
        <ProfileInfo />
        <ShopSettings />
        <BottomNavBar />
      </div>
    </ProfileProvider>
  );
};
```

#### ProfileInfo.jsx
**Размер**: ~250 строк

**Ответственность**:
- User information display
- Team members list
- Invite colleague modal
- Edit/delete member UI

**State** (через useTeamManagement):
- inviteModal state
- editingMember state
- deleteConfirmation state

**UI Sections**:
1. User info card
2. Team members table
3. Invite button + modal
4. Pending invitations list

**Пример**:
```javascript
const ProfileInfo = () => {
  const { teamMembers, teamInvitations, refreshTeam } = useProfile();
  const {
    handleInvite,
    handleEditRole,
    handleDeleteMember,
    handleCancelInvitation,
    inviteState
  } = useTeamManagement(refreshTeam);

  return (
    <div className="profile-info">
      <UserCard />
      <TeamMembersList
        members={teamMembers}
        onEdit={handleEditRole}
        onDelete={handleDeleteMember}
      />
      <InviteModal
        isOpen={inviteState.showModal}
        onSubmit={handleInvite}
      />
      <InvitationsList
        invitations={teamInvitations}
        onCancel={handleCancelInvitation}
      />
    </div>
  );
};
```

#### ShopSettings.jsx
**Размер**: ~350 строк

**Ответственность**:
- Shop configuration display/edit
- Working hours management
- Delivery settings
- Edit mode logic

**Sections**:
1. Shop info (name, address, phone, email)
2. Working hours (morning/evening periods)
3. Delivery zones & minimum order
4. Edit/Save/Cancel buttons

**State**:
```javascript
const [isEditing, setIsEditing] = useState(false);
const [editedSettings, setEditedSettings] = useState(null);
const [isSaving, setIsSaving] = useState(false);
const [validationErrors, setValidationErrors] = useState({});
```

**Пример**:
```javascript
const ShopSettings = () => {
  const { shopSettings, refreshShop } = useProfile();
  const [isEditing, setIsEditing] = useState(false);
  const [editedSettings, setEditedSettings] = useState(null);

  const handleStartEditing = () => { /* ... */ };
  const handleSaveSettings = async () => { /* ... */ };
  const handleCancelEditing = () => { /* ... */ };

  return (
    <div className="shop-settings">
      <ShopInfoSection
        settings={isEditing ? editedSettings : shopSettings}
        isEditing={isEditing}
        onChange={updateLocalSetting}
      />
      <WorkingHoursSection
        hours={isEditing ? editedSettings.working_hours : shopSettings.working_hours}
        isEditing={isEditing}
        onChange={updateWorkingHours}
      />
      <DeliverySection
        delivery={isEditing ? editedSettings.delivery : shopSettings.delivery}
        isEditing={isEditing}
        onChange={updateDeliverySettings}
      />
      {isEditing ? (
        <SaveCancelButtons onSave={handleSaveSettings} onCancel={handleCancelEditing} />
      ) : (
        <EditButton onClick={handleStartEditing} />
      )}
    </div>
  );
};
```

#### hooks/useTeamManagement.js
**Размер**: ~120 строк

**Ответственность**:
- Team invitation logic
- Role editing
- Member deletion
- Invitation cancellation

**Interface**:
```javascript
const useTeamManagement = (onSuccess) => {
  const [inviteState, setInviteState] = useState({
    showModal: false,
    showSuccessModal: false,
    invitationCode: '',
    loading: false,
    newColleague: { name: '', phone: '', role: 'MANAGER' }
  });

  const [editState, setEditState] = useState({
    editingMemberId: null,
    editedRole: '',
    loading: false
  });

  const handleInvite = async (colleagueData) => {
    // API call: profileAPI.inviteTeamMember()
    // Show success modal with invitation code
    // Call onSuccess() to refresh team list
  };

  const handleEditRole = async (userId, newRole) => {
    // API call: profileAPI.changeTeamMemberRole()
    // Call onSuccess() to refresh team list
  };

  const handleDeleteMember = async (userId) => {
    // API call: profileAPI.removeTeamMember()
    // Call onSuccess() to refresh team list
  };

  const handleCancelInvitation = async (invitationId) => {
    // API call: profileAPI.cancelInvitation()
    // Call onSuccess() to refresh invitations
  };

  return {
    inviteState,
    editState,
    handleInvite,
    handleEditRole,
    handleDeleteMember,
    handleCancelInvitation
  };
};
```

### План миграции (шаги)

1. **Создать ProfileContext.jsx**
   - Define context schema
   - Implement ProfileProvider with state
   - Implement refresh methods (API calls)
   - Export useProfile hook

2. **Создать hooks/useTeamManagement.js**
   - Extract invite logic from Profile.jsx
   - Extract edit/delete logic
   - Add state management for modals
   - Return handlers and state

3. **Создать ShopSettings.jsx**
   - Extract shop settings section
   - Extract working hours logic
   - Extract delivery settings logic
   - Implement edit mode
   - Use useProfile for data

4. **Создать ProfileInfo.jsx**
   - Extract user info display
   - Extract team members list
   - Extract invite modal
   - Use useProfile + useTeamManagement

5. **Обновить Profile.jsx**
   - Remove extracted logic
   - Keep only layout & navigation
   - Wrap with ProfileProvider
   - Render ProfileInfo and ShopSettings

6. **Обновить импорты**
   - Check if Profile is imported elsewhere
   - Update imports if needed

7. **Тестировать**
   - `npm run build` - check for errors
   - `npm run dev` - manual testing
   - Test all team management flows
   - Test shop settings editing

### Риски и митигация

**Риск 1: Props drilling если не использовать Context**
- ✅ Митигация: Используем Context API

**Риск 2: Сложная логика shop settings validation**
- ✅ Митигация: Сохраняем всю validation логику в ShopSettings.jsx

**Риск 3: Модалы могут сломаться при разделении**
- ✅ Митигация: Тщательно переносим state для модалов в useTeamManagement

**Оценка времени**: 2-3 часа
**Сложность**: Низкая

---

## 📋 TASK 4: OrderDetail.jsx (1261 строка → 14 файлов)

### Цель
Разделить монолитный OrderDetail.jsx на модульную структуру с 3 custom hooks и Context API.

### Новая структура
```
frontend/src/components/orders/
├── OrderContext.jsx               (100 lines) - Context для order data
├── OrderDetail.jsx                (200 lines) - Main orchestrator
├── OrderInfo.jsx                  (150 lines) - Basic info display
├── OrderStatusManager.jsx         (180 lines) - Status dropdown + next status
├── OrderEditor.jsx                (200 lines) - Edit mode form
├── OrderItemsList.jsx             (120 lines) - Items table
├── OrderPhotos.jsx                (200 lines) - Photo upload/delete gallery
├── OrderHistory.jsx               (150 lines) - Change history timeline
├── OrderAssignments.jsx           (180 lines) - Responsible + courier dropdowns
├── OrderPayments.jsx              (150 lines) - Kaspi refund section
└── hooks/
    ├── useOrderData.js            (120 lines) - Fetch & refresh order
    ├── useOrderPhotos.js          (100 lines) - Upload/delete photos
    └── useOrderStatus.js          (100 lines) - Status state machine logic
```

### Текущее состояние
- **Размер**: 1,261 строка
- **useState**: 21 hooks
- **Обработчики**: 15 функций
- **Функциональность**:
  - Order info display & editing
  - Status management (state machine logic)
  - Photo upload/delete (Cloudflare R2)
  - Team assignments (responsible person, courier)
  - Order history tracking
  - Kaspi Pay refunds
  - Delivery time selection

### Разделение функциональности

#### OrderContext.jsx (новый файл)
**Ответственность**: Централизованное управление состоянием заказа

**State**:
```javascript
{
  orderData: null,        // Full order object
  loading: true,
  error: null,
  isEditing: false,       // Edit mode toggle
  recipientInfo: null     // Parsed recipient info
}
```

**Методы**:
- `refreshOrder()` - Reload order data
- `setOrderData(data)` - Update order
- `toggleEdit()` - Switch edit mode
- `updateField(field, value)` - Update single field

**Использование**:
```javascript
export const OrderProvider = ({ orderId, children }) => {
  const [state, setState] = useState(initialState);

  useEffect(() => {
    fetchOrder(orderId);
  }, [orderId]);

  const refreshOrder = async () => { /* ... */ };
  const toggleEdit = () => setState(prev => ({ ...prev, isEditing: !prev.isEditing }));

  return (
    <OrderContext.Provider value={{ ...state, refreshOrder, toggleEdit }}>
      {children}
    </OrderContext.Provider>
  );
};

export const useOrder = () => useContext(OrderContext);
```

#### OrderDetail.jsx (главный оркестратор)
**Размер**: ~200 строк

**Ответственность**:
- Layout & header
- Back navigation
- Copy tracking link
- Render all sections

**Структура**:
```javascript
const OrderDetail = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { orderData, loading, error } = useOrder();

  const handleBack = () => navigate(-1);
  const handleCopyTrackingLink = async () => { /* ... */ };

  if (loading) return <Spinner />;
  if (error) return <ErrorView error={error} />;

  return (
    <OrderProvider orderId={orderId}>
      <div className="figma-container">
        <Header onBack={handleBack} />
        <OrderInfo />
        <OrderStatusManager />
        <OrderItemsList />
        <OrderPhotos />
        <OrderAssignments />
        <OrderHistory />
        <OrderPayments />
        <BottomNavBar />
      </div>
    </OrderProvider>
  );
};
```

#### hooks/useOrderData.js
**Размер**: ~120 строк

**Ответственность**: Загрузка и обновление данных заказа

**Interface**:
```javascript
const useOrderData = (orderId) => {
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recipientInfo, setRecipientInfo] = useState(null);

  const fetchOrder = async () => {
    try {
      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);

      // Parse recipient info from notes
      const recipientMatch = formattedOrder.notes.match(/Получатель: (.+?), тел: (.+?)(?:\n|$)/);
      if (recipientMatch) {
        setRecipientInfo({
          name: recipientMatch[1],
          phone: recipientMatch[2]
        });
      }

      setOrderData(formattedOrder);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrder();
  }, [orderId]);

  const refreshOrder = () => fetchOrder();

  return {
    orderData,
    recipientInfo,
    loading,
    error,
    refreshOrder
  };
};
```

#### hooks/useOrderPhotos.js
**Размер**: ~100 строк

**Ответственность**: Upload/delete фото через Cloudflare R2

**Interface**:
```javascript
const useOrderPhotos = (orderId, onSuccess) => {
  const [isUploading, setIsUploading] = useState(false);
  const photoFileInputRef = useRef(null);

  const handlePhotoClick = () => {
    photoFileInputRef.current?.click();
  };

  const handlePhotoSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('Размер файла не должен превышать 10 МБ');
      return;
    }

    try {
      setIsUploading(true);
      await ordersAPI.uploadOrderPhoto(orderId, file);
      onSuccess(); // Refresh order data
    } catch (err) {
      alert(`Ошибка загрузки: ${err.message}`);
    } finally {
      setIsUploading(false);
      event.target.value = '';
    }
  };

  const handlePhotoDelete = async () => {
    if (!confirm('Удалить фото?')) return;

    try {
      await ordersAPI.deleteOrderPhoto(orderId);
      onSuccess(); // Refresh order data
    } catch (err) {
      alert(`Ошибка удаления: ${err.message}`);
    }
  };

  return {
    isUploading,
    photoFileInputRef,
    handlePhotoClick,
    handlePhotoSelect,
    handlePhotoDelete
  };
};
```

#### hooks/useOrderStatus.js
**Размер**: ~100 строк

**Ответственность**: State machine логика для статусов заказа

**Interface**:
```javascript
const useOrderStatus = (orderData, onSuccess) => {
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isStatusDropdownOpen, setIsStatusDropdownOpen] = useState(false);

  const availableStatuses = [
    { id: 'new', label: 'Новый' },
    { id: 'paid', label: 'Оплачен' },
    { id: 'accepted', label: 'Принят' },
    { id: 'assembled', label: 'Собран' },
    { id: 'in_delivery', label: 'В пути' },
    { id: 'delivered', label: 'Доставлен' },
    { id: 'cancelled', label: 'Отменён' }
  ];

  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      'new': 'accepted',
      'paid': 'accepted',
      'accepted': 'assembled',
      'assembled': 'in_delivery',
      'in_delivery': 'delivered',
      'delivered': null,
      'cancelled': null
    };
    return statusFlow[currentStatus] || null;
  };

  const getNextStatusButtonText = (currentStatus) => {
    const buttonTexts = {
      'new': 'Принять заказ',
      'paid': 'Принять заказ',
      'accepted': 'Собрать',
      'assembled': 'Передать курьеру',
      'in_delivery': 'Доставлен',
      'delivered': null
    };
    return buttonTexts[currentStatus] || null;
  };

  const handleStatusChange = async (newStatus) => {
    try {
      setIsUpdatingStatus(true);
      await ordersAPI.updateOrderStatus(orderData.id, newStatus);
      setIsStatusDropdownOpen(false);
      onSuccess(); // Refresh order data
    } catch (err) {
      alert(`Ошибка обновления статуса: ${err.message}`);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleNextStatus = async () => {
    const nextStatus = getNextStatus(orderData.status);
    if (nextStatus) {
      await handleStatusChange(nextStatus);
    }
  };

  const handleCancelOrder = async () => {
    if (!confirm('Отменить заказ?')) return;
    await handleStatusChange('cancelled');
  };

  return {
    availableStatuses,
    isStatusDropdownOpen,
    setIsStatusDropdownOpen,
    isUpdatingStatus,
    getNextStatus,
    getNextStatusButtonText,
    handleStatusChange,
    handleNextStatus,
    handleCancelOrder
  };
};
```

#### OrderInfo.jsx
**Размер**: ~150 строк

**Ответственность**: Отображение базовой информации о заказе (read-only)

**Sections**:
1. Order number & tracking ID
2. Customer name & phone
3. Delivery address
4. Delivery date & time
5. Recipient info (if different from customer)

**Пример**:
```javascript
const OrderInfo = () => {
  const { orderData, recipientInfo } = useOrder();

  return (
    <div className="order-info">
      <InfoRow label="Номер заказа" value={orderData.orderNumber} />
      <InfoRow label="Tracking ID" value={orderData.tracking_id} copyable />
      <InfoRow label="Заказчик" value={orderData.customerName} />
      <InfoRow label="Телефон" value={orderData.phone} />
      <InfoRow label="Адрес доставки" value={orderData.delivery_address} />
      <InfoRow label="Дата и время" value={orderData.delivery_date} />
      {recipientInfo && (
        <>
          <InfoRow label="Получатель" value={recipientInfo.name} />
          <InfoRow label="Телефон получателя" value={recipientInfo.phone} />
        </>
      )}
    </div>
  );
};
```

#### OrderStatusManager.jsx
**Размер**: ~180 строк

**Ответственность**: Управление статусом заказа

**UI Elements**:
- Status badge (color-coded)
- Status dropdown (для ручного изменения)
- "Next status" button (state machine)
- Cancel button

**Пример**:
```javascript
const OrderStatusManager = () => {
  const { orderData, refreshOrder } = useOrder();
  const {
    availableStatuses,
    isStatusDropdownOpen,
    setIsStatusDropdownOpen,
    isUpdatingStatus,
    getNextStatusButtonText,
    handleStatusChange,
    handleNextStatus,
    handleCancelOrder
  } = useOrderStatus(orderData, refreshOrder);

  const nextStatusText = getNextStatusButtonText(orderData.status);

  return (
    <div className="order-status-manager">
      <StatusBadge status={orderData.status} label={orderData.statusLabel} />

      <Dropdown
        isOpen={isStatusDropdownOpen}
        onToggle={() => setIsStatusDropdownOpen(!isStatusDropdownOpen)}
      >
        {availableStatuses.map(status => (
          <DropdownItem
            key={status.id}
            onClick={() => handleStatusChange(status.id)}
            selected={status.id === orderData.status}
          >
            {status.label}
          </DropdownItem>
        ))}
      </Dropdown>

      {nextStatusText && (
        <Button
          onClick={handleNextStatus}
          loading={isUpdatingStatus}
          variant="primary"
        >
          {nextStatusText}
        </Button>
      )}

      {orderData.status !== 'cancelled' && orderData.status !== 'delivered' && (
        <Button
          onClick={handleCancelOrder}
          variant="danger"
        >
          Отменить заказ
        </Button>
      )}
    </div>
  );
};
```

#### OrderEditor.jsx
**Размер**: ~200 строк

**Ответственность**: Edit mode для изменения деталей заказа

**Editable Fields**:
- Customer name
- Phone
- Delivery address
- Delivery date
- Delivery time (time slots selector)
- Notes

**Пример**:
```javascript
const OrderEditor = () => {
  const { orderData, isEditing, toggleEdit, refreshOrder } = useOrder();
  const [editedFields, setEditedFields] = useState({});
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');

  const handleSaveOrder = async () => {
    try {
      const updateData = {};

      if (editedFields.customerName) updateData.customerName = editedFields.customerName;
      if (editedFields.phone) updateData.phone = editedFields.phone;
      if (editedFields.delivery_address) updateData.delivery_address = editedFields.delivery_address;

      // Handle delivery date/time
      if (selectedDate && selectedTime) {
        const [startTime] = selectedTime.split('-');
        const [hours, minutes] = startTime.split(':');
        // Construct ISO datetime...
        updateData.delivery_date = /* ... */;
      }

      await ordersAPI.updateOrder(orderData.id, updateData);
      toggleEdit();
      refreshOrder();
    } catch (err) {
      alert(`Ошибка сохранения: ${err.message}`);
    }
  };

  if (!isEditing) return null;

  return (
    <div className="order-editor">
      <Input
        label="Имя заказчика"
        value={editedFields.customerName ?? orderData.customerName}
        onChange={(e) => setEditedFields({ ...editedFields, customerName: e.target.value })}
      />
      <Input
        label="Телефон"
        value={editedFields.phone ?? orderData.phone}
        onChange={(e) => setEditedFields({ ...editedFields, phone: e.target.value })}
      />
      <TextArea
        label="Адрес доставки"
        value={editedFields.delivery_address ?? orderData.delivery_address}
        onChange={(e) => setEditedFields({ ...editedFields, delivery_address: e.target.value })}
      />
      <DeliveryDateTimeSelector
        selectedDate={selectedDate}
        selectedTime={selectedTime}
        onDateChange={setSelectedDate}
        onTimeChange={setSelectedTime}
      />
      <div className="editor-actions">
        <Button onClick={handleSaveOrder} variant="primary">Сохранить</Button>
        <Button onClick={toggleEdit} variant="secondary">Отменить</Button>
      </div>
    </div>
  );
};
```

#### OrderItemsList.jsx
**Размер**: ~120 строк

**Ответственность**: Список товаров в заказе

**Display**:
- Product name
- Quantity
- Price per item
- Total per item
- Total order amount

**Пример**:
```javascript
const OrderItemsList = () => {
  const { orderData } = useOrder();

  return (
    <div className="order-items">
      <h3>Товары</h3>
      <table>
        <thead>
          <tr>
            <th>Товар</th>
            <th>Кол-во</th>
            <th>Цена</th>
            <th>Сумма</th>
          </tr>
        </thead>
        <tbody>
          {orderData.items.map((item, index) => (
            <tr key={index}>
              <td>
                <div className="item-name">{item.name}</div>
                {item.description && (
                  <div className="item-description">{item.description}</div>
                )}
              </td>
              <td>{item.quantity}</td>
              <td>{item.price}</td>
              <td>{item.total}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan="3"><strong>Итого:</strong></td>
            <td><strong>{orderData.total}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
};
```

#### OrderPhotos.jsx
**Размер**: ~200 строк

**Ответственность**: Фото заказа (upload/delete/preview)

**Features**:
- Upload button (click to select file)
- Photo preview/gallery
- Delete confirmation
- Upload progress indicator

**Пример**:
```javascript
const OrderPhotos = () => {
  const { orderData, refreshOrder } = useOrder();
  const {
    isUploading,
    photoFileInputRef,
    handlePhotoClick,
    handlePhotoSelect,
    handlePhotoDelete
  } = useOrderPhotos(orderData.id, refreshOrder);

  return (
    <div className="order-photos">
      <h3>Фото заказа</h3>

      <input
        type="file"
        ref={photoFileInputRef}
        accept="image/*"
        onChange={handlePhotoSelect}
        style={{ display: 'none' }}
      />

      {orderData.photos && orderData.photos.length > 0 ? (
        <div className="photo-gallery">
          {orderData.photos.map((photo, index) => (
            <div key={index} className="photo-item">
              <img src={photo.url} alt={photo.label || 'Order photo'} />
              {photo.feedback && (
                <div className="photo-feedback">{photo.feedback}</div>
              )}
              <Button onClick={handlePhotoDelete} variant="danger" size="sm">
                Удалить
              </Button>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-photos">
          <p>Фото пока не загружено</p>
        </div>
      )}

      <Button
        onClick={handlePhotoClick}
        loading={isUploading}
        variant="secondary"
      >
        {isUploading ? 'Загрузка...' : 'Загрузить фото'}
      </Button>
    </div>
  );
};
```

#### OrderHistory.jsx
**Размер**: ~150 строк

**Ответственность**: История изменений заказа

**Display**:
- Timeline of changes
- Field name (formatted)
- Old value → New value
- Timestamp (formatted)
- Who changed (customer/admin)

**Пример**:
```javascript
const OrderHistory = () => {
  const { orderData } = useOrder();
  const [orderHistory, setOrderHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await ordersAPI.getOrderHistory(orderData.id);
        setOrderHistory(history);
      } catch (err) {
        console.error('Error loading history:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [orderData.id]);

  const formatFieldName = (fieldName) => {
    const fieldNames = {
      'status': 'Статус',
      'delivery_address': 'Адрес доставки',
      'delivery_date': 'Дата доставки',
      'assigned_to': 'Ответственный',
      'courier': 'Курьер',
      // ... etc
    };
    return fieldNames[fieldName] || fieldName;
  };

  const formatTimestamp = (timestamp) => {
    // "Сегодня, 14:30" / "Вчера, 12:00" / "15 окт, 10:45"
  };

  if (loading) return <Spinner />;

  return (
    <div className="order-history">
      <h3>История изменений</h3>
      <div className="timeline">
        {orderHistory.map((record, index) => (
          <div key={index} className="timeline-item">
            <div className="timeline-time">{formatTimestamp(record.changed_at)}</div>
            <div className="timeline-content">
              <strong>{formatFieldName(record.field_name)}</strong>
              <div className="change-values">
                <span className="old-value">{record.old_value || '—'}</span>
                <span className="arrow">→</span>
                <span className="new-value">{record.new_value}</span>
              </div>
              <div className="changed-by">
                {record.changed_by === 'admin' ? 'Администратор' : 'Клиент'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### OrderAssignments.jsx
**Размер**: ~180 строк

**Ответственность**: Назначение ответственного и курьера

**Features**:
- Responsible person dropdown
- Courier dropdown
- Team members loading
- Assignment handlers
- Role-based filtering (FLORIST/MANAGER for responsible, COURIER for courier)

**Пример**:
```javascript
const OrderAssignments = () => {
  const { orderData, refreshOrder } = useOrder();
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isResponsibleDropdownOpen, setIsResponsibleDropdownOpen] = useState(false);
  const [isCourierDropdownOpen, setIsCourierDropdownOpen] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  useEffect(() => {
    const fetchTeam = async () => {
      try {
        const users = await profileAPI.getTeamMembers({ limit: 50 });
        setTeamMembers(users);
      } catch (err) {
        console.error('Error loading team:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTeam();
  }, []);

  const handleAssignResponsible = async (userId) => {
    try {
      setIsAssigning(true);
      await ordersAPI.assignResponsible(orderData.id, userId);
      setIsResponsibleDropdownOpen(false);
      refreshOrder();
    } catch (err) {
      alert(`Ошибка назначения: ${err.message}`);
    } finally {
      setIsAssigning(false);
    }
  };

  const handleAssignCourier = async (userId) => {
    try {
      setIsAssigning(true);
      await ordersAPI.assignCourier(orderData.id, userId);
      setIsCourierDropdownOpen(false);
      refreshOrder();
    } catch (err) {
      alert(`Ошибка назначения: ${err.message}`);
    } finally {
      setIsAssigning(false);
    }
  };

  // Filter team members by role
  const responsibleCandidates = teamMembers.filter(u =>
    ['DIRECTOR', 'MANAGER', 'FLORIST'].includes(u.role)
  );
  const courierCandidates = teamMembers.filter(u => u.role === 'COURIER');

  return (
    <div className="order-assignments">
      <h3>Назначения</h3>

      <div className="assignment-row">
        <label>Ответственный:</label>
        <Dropdown
          isOpen={isResponsibleDropdownOpen}
          onToggle={() => setIsResponsibleDropdownOpen(!isResponsibleDropdownOpen)}
          trigger={orderData.assigned_to_name || 'Не назначен'}
        >
          {responsibleCandidates.map(user => (
            <DropdownItem
              key={user.id}
              onClick={() => handleAssignResponsible(user.id)}
            >
              {user.name} ({user.role})
            </DropdownItem>
          ))}
        </Dropdown>
      </div>

      <div className="assignment-row">
        <label>Курьер:</label>
        <Dropdown
          isOpen={isCourierDropdownOpen}
          onToggle={() => setIsCourierDropdownOpen(!isCourierDropdownOpen)}
          trigger={orderData.courier_name || 'Не назначен'}
        >
          {courierCandidates.map(user => (
            <DropdownItem
              key={user.id}
              onClick={() => handleAssignCourier(user.id)}
            >
              {user.name}
            </DropdownItem>
          ))}
        </Dropdown>
      </div>
    </div>
  );
};
```

#### OrderPayments.jsx
**Размер**: ~150 строк

**Ответственность**: Kaspi Pay информация и возвраты

**Features**:
- Payment status display
- Refund amount input
- Refund button
- Payment timestamps

**Пример**:
```javascript
const OrderPayments = () => {
  const { orderData, refreshOrder } = useOrder();
  const [refundAmount, setRefundAmount] = useState('');
  const [isRefunding, setIsRefunding] = useState(false);

  const handleKaspiRefund = async () => {
    const amount = parseFloat(refundAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('Введите корректную сумму возврата');
      return;
    }

    if (!confirm(`Вернуть ${amount} ₸ через Kaspi Pay?`)) return;

    try {
      setIsRefunding(true);
      // API call to Kaspi refund endpoint
      await fetch(`http://localhost:8014/api/v1/kaspi/refund/${orderData.kaspi_payment_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount })
      });
      refreshOrder();
      setRefundAmount('');
      alert('Возврат успешно выполнен');
    } catch (err) {
      alert(`Ошибка возврата: ${err.message}`);
    } finally {
      setIsRefunding(false);
    }
  };

  if (orderData.payment_method !== 'kaspi') return null;

  return (
    <div className="order-payments">
      <h3>Kaspi Pay</h3>

      <InfoRow label="Статус платежа" value={orderData.kaspi_payment_status} />
      <InfoRow label="Payment ID" value={orderData.kaspi_payment_id} />

      {orderData.kaspi_payment_created_at && (
        <InfoRow
          label="Создан"
          value={new Date(orderData.kaspi_payment_created_at).toLocaleString('ru-RU')}
        />
      )}

      {orderData.kaspi_payment_completed_at && (
        <InfoRow
          label="Завершён"
          value={new Date(orderData.kaspi_payment_completed_at).toLocaleString('ru-RU')}
        />
      )}

      {orderData.kaspi_payment_status === 'PAID' && (
        <div className="refund-section">
          <h4>Возврат средств</h4>
          <Input
            type="number"
            label="Сумма возврата (₸)"
            value={refundAmount}
            onChange={(e) => setRefundAmount(e.target.value)}
            placeholder="0.00"
          />
          <Button
            onClick={handleKaspiRefund}
            loading={isRefunding}
            variant="danger"
          >
            Выполнить возврат
          </Button>
        </div>
      )}
    </div>
  );
};
```

### План миграции (шаги)

1. **Создать OrderContext.jsx**
   - Define context schema
   - Implement OrderProvider with state
   - Implement refresh/update methods
   - Export useOrder hook

2. **Создать hooks/useOrderData.js**
   - Extract fetch logic
   - Parse recipient info
   - Return order data + loading/error states

3. **Создать hooks/useOrderPhotos.js**
   - Extract photo upload logic
   - Extract photo delete logic
   - Return handlers + upload state

4. **Создать hooks/useOrderStatus.js**
   - Extract status state machine
   - Implement getNextStatus logic
   - Return status handlers

5. **Создать OrderInfo.jsx**
   - Simple read-only component
   - Display customer, delivery, recipient info
   - Use useOrder context

6. **Создать OrderItemsList.jsx**
   - Simple table component
   - Display items + total
   - Use useOrder context

7. **Создать OrderHistory.jsx**
   - Fetch history via API
   - Format timestamps & field names
   - Timeline UI

8. **Создать OrderPhotos.jsx**
   - Use useOrderPhotos hook
   - Photo gallery + upload button
   - Delete confirmation

9. **Создать OrderStatusManager.jsx**
   - Use useOrderStatus hook
   - Status dropdown + next status button
   - Cancel button

10. **Создать OrderAssignments.jsx**
    - Fetch team members
    - Responsible + courier dropdowns
    - Assignment handlers

11. **Создать OrderEditor.jsx**
    - Edit mode form
    - Delivery date/time selector
    - Save/cancel handlers

12. **Создать OrderPayments.jsx**
    - Kaspi payment info
    - Refund functionality

13. **Обновить OrderDetail.jsx**
    - Remove all extracted logic
    - Keep only layout & navigation
    - Wrap with OrderProvider
    - Render all child components

14. **Тестировать**
    - `npm run build` - check for errors
    - `npm run dev` - manual testing
    - Test all order operations:
      - View order info
      - Change status
      - Upload/delete photo
      - Edit order
      - Assign team members
      - View history
      - Kaspi refund

### Риски и митигация

**Риск 1: State machine логика может сломаться**
- ✅ Митигация: useOrderStatus hook изолирует всю state machine логику

**Риск 2: Photo upload через Cloudflare R2 может иметь CORS issues**
- ✅ Митигация: Тщательно тестируем upload, сохраняем всю логику в useOrderPhotos

**Риск 3: Много зависимостей между компонентами**
- ✅ Митигация: Context API устраняет prop drilling

**Риск 4: Edit mode имеет сложную валидацию**
- ✅ Митигация: Вся validation логика остаётся в OrderEditor.jsx

**Оценка времени**: 4-5 часов
**Сложность**: Средняя

---

## 🎯 Общий план выполнения

### Последовательность

1. **Task 3: Profile.jsx** (2-3 часа)
   - Easier component
   - Builds confidence
   - Tests Context API pattern

2. **Task 4: OrderDetail.jsx** (4-5 часов)
   - More complex
   - More components
   - More custom hooks
   - Builds on Task 3 experience

### Критерии успеха

**После Task 3:**
- ✅ Frontend build успешен
- ✅ Profile page работает в dev mode
- ✅ Team management flows работают
- ✅ Shop settings editing работает
- ✅ All files < 350 lines

**После Task 4:**
- ✅ Frontend build успешен
- ✅ OrderDetail page работает в dev mode
- ✅ Status changes работают
- ✅ Photo upload/delete работает
- ✅ Order editing работает
- ✅ Team assignments работают
- ✅ All files < 250 lines

### Команды тестирования

```bash
# Frontend build test
cd frontend
npm run build

# Frontend dev server
npm run dev

# Manual testing checklist:
# Profile page:
# - [ ] View user info
# - [ ] Invite team member
# - [ ] Edit member role
# - [ ] Delete member
# - [ ] Edit shop settings
# - [ ] Save shop settings

# OrderDetail page:
# - [ ] View order info
# - [ ] Change status manually
# - [ ] Use "Next status" button
# - [ ] Upload photo
# - [ ] Delete photo
# - [ ] Edit order
# - [ ] Save edited order
# - [ ] Assign responsible
# - [ ] Assign courier
# - [ ] View history
# - [ ] Kaspi refund (if applicable)
```

---

## 📝 Заметки для выполнения

### Context API Best Practices
- ✅ Используем отдельный Provider для каждого domain (Profile, Order)
- ✅ Экспортируем custom hook для доступа к context (`useProfile`, `useOrder`)
- ✅ Provider оборачивает только необходимые компоненты (не весь App)
- ✅ Избегаем лишних re-renders через useMemo/useCallback если нужно

### Custom Hooks Best Practices
- ✅ Один hook = одна ответственность
- ✅ Возвращаем объект (не массив) для лучшей читаемости
- ✅ Используем префикс `use` для всех hooks
- ✅ Hooks могут вызывать другие hooks

### Component Structure
- ✅ Props минимальны благодаря Context API
- ✅ Каждый компонент фокусируется на UI одной секции
- ✅ Business logic в hooks, UI в components
- ✅ Переиспользуемые UI элементы (Button, Input, Dropdown) уже существуют

### Import Organization
```javascript
// React & hooks
import React, { useState, useEffect } from 'react';

// Router
import { useNavigate, useParams } from 'react-router-dom';

// Contexts & hooks
import { useProfile } from './ProfileContext';
import { useTeamManagement } from './hooks/useTeamManagement';

// APIs
import { profileAPI, shopAPI, ordersAPI } from '../../services';

// Components
import BottomNavBar from '../BottomNavBar';
import Button from '../Button';

// Styles
import './Profile.css';
```

---

## ✅ Чеклист перед началом

- [ ] Pull latest changes: `git pull origin main`
- [ ] Убедиться что frontend build работает: `cd frontend && npm run build`
- [ ] Убедиться что dev server запускается: `npm run dev`
- [ ] Проверить что Tasks 1-2 не сломались после pull
- [ ] Создать ветку для Tasks 3-4: `git checkout -b refactor/tasks-3-4`

---

## 📦 Ожидаемые результаты

**Файлы создано**: 20 новых файлов
- Profile: 6 files (1 context + 4 components + 1 hook)
- OrderDetail: 14 files (1 context + 10 components + 3 hooks)

**Коммиты**: 2
1. "refactor: Split Profile.jsx into modular components with Context API"
2. "refactor: Split OrderDetail.jsx into 10 components with custom hooks"

**Метрики**:
- Средний размер файла: ~150 lines
- Все файлы < 350 lines
- Zero breaking changes
- 100% backward compatibility

**Build time**: Should remain ~2s or faster

---

**Дата последнего обновления**: 23 октября 2025
**Статус плана**: ✅ УТВЕРЖДЁН
