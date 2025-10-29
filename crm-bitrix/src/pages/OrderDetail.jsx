import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services';
import { useTeamMembers } from '../hooks/useTeamMembers';
import LoadingSpinner from '../components/LoadingSpinner';
import { Badge, Button } from '../components/ui';
import PriceFormatter from '../components/PriceFormatter';
import ImageModal from '../components/ImageModal';
import StatusTimeline from '../components/StatusTimeline';
import PhotoUploadSection from '../components/PhotoUploadSection';
import DropdownField from '../components/DropdownField';
import WhatsAppIcon from '../components/WhatsAppIcon';
import { useToast } from '../components/ToastProvider';
import { formatDeliveryDateTime } from '../services/formatters';
import { ArrowLeft, Copy, CheckCircle, Share2, Upload, ChevronDown } from 'lucide-react';

const STATUS_OPTIONS = [
  { value: 'NEW', label: 'Новый' },
  { value: 'ACCEPTED', label: 'Принят' },
  { value: 'IN_PRODUCTION', label: 'Собран' },
  { value: 'IN_DELIVERY', label: 'В доставке' },
  { value: 'DELIVERED', label: 'Доставлен' },
  { value: 'CANCELLED', label: 'Отменён' },
];

export function OrderDetail() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { showError, showSuccess } = useToast();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  // Photo modal state
  const [photoModal, setPhotoModal] = useState({ isOpen: false, imageUrl: null, imageAlt: 'Order photo' });

  // Copy to clipboard state
  const [copiedId, setCopiedId] = useState(null);

  // Photo upload state
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  // Executor state
  const [executorStatus, setExecutorStatus] = useState(null);
  const [executorResponsible, setExecutorResponsible] = useState(null);

  // Expanded items state
  const [expandedItems, setExpandedItems] = useState(new Set());

  // History expanded state
  const [historyExpanded, setHistoryExpanded] = useState(false);

  // Team members from hook
  const { managers, loadingTeam } = useTeamMembers();

  useEffect(() => {
    loadOrder().catch(err => {
      console.error('Error loading order:', err);
    });
  }, [orderId]);

  useEffect(() => {
    if (order && order.raw) {
      setExecutorResponsible(order.raw.responsibleId?.toString() || '');
    }
  }, [order]);

  async function loadOrder() {
    try {
      setLoading(true);
      const data = await ordersAPI.getOrder(orderId);
      setOrder(data);
      setError(null);
    } catch (err) {
      const message = err.message || 'Ошибка при загрузке заказа';
      setError(message);
      showError(message);
    } finally {
      setLoading(false);
    }
  }

  async function updateStatus(newStatus) {
    try {
      setUpdating(true);
      const updated = await ordersAPI.updateOrderStatus(orderId, newStatus);
      setOrder(updated);
      showSuccess('Статус заказа обновлен');
    } catch (err) {
      showError(err.message || 'Ошибка при обновлении статуса');
    } finally {
      setUpdating(false);
    }
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  }

  async function handlePhotoUpload(file) {
    try {
      setUploadingPhoto(true);

      // Upload photo to Cloudflare R2 via backend
      const response = await ordersAPI.uploadPhoto(orderId, file);

      // Update local state with uploaded photo URL
      if (response.photo_url) {
        setUploadedPhoto(response.photo_url);
      }

      // Reload order to get updated status (should be ASSEMBLED now)
      await loadOrder();

      showSuccess('Фото загружено и статус заказа обновлен');
    } catch (err) {
      console.error('Error uploading photo:', err);
      showError('Ошибка при загрузке фото');
    } finally {
      setUploadingPhoto(false);
    }
  }

  function handleShareOrder() {
    const shareUrl = order?.raw?.raw?.urls?.status || order?.raw?.urls?.status || `${window.location.origin}/orders/${orderId}`;
    copyToClipboard(shareUrl);
    showSuccess('Ссылка скопирована в буфер обмена');
  }

  // Decode Unicode escape sequences
  function decodeUnicodeEscapes(text) {
    if (!text) return text;
    try {
      return text.replace(/\\u[\dA-Fa-f]{4}/g, (match) => {
        return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
      });
    } catch (e) {
      console.error('Failed to decode Unicode escapes:', e);
      return text;
    }
  }

  // Map order status to Badge status prop
  function getStatusForBadge(statusKey) {
    const statusMap = {
      'NEW': 'new',
      'PAID': 'paid',
      'ACCEPTED': 'accepted',
      'IN_PRODUCTION': 'assembled',
      'IN_DELIVERY': 'delivered',
      'DELIVERED': 'delivered'
    };
    return statusMap[statusKey?.toUpperCase()] || 'new';
  }

  // Dynamic team member options
  const responsibleOptions = [
    { value: '', label: 'Выбрать' },
    ...managers.map(m => ({ value: m.id.toString(), label: m.name }))
  ];

  if (loading) return <LoadingSpinner message="Загрузка заказа..." />;

  if (error || !order) {
    return (
      <div className="figma-container bg-white flex items-center justify-center">
        <div className="p-6 text-center">
          <h2 className="text-lg font-sans font-bold text-red-600 mb-2">Ошибка</h2>
          <p className="text-grey-disabled mb-4">{error || 'Заказ не найден'}</p>
          <Button
            variant="primary"
            onClick={() => navigate('/orders-new')}
            className="w-full"
          >
            Вернуться к заказам
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header - Figma Design Style */}
      <div className="flex items-center px-4 mt-4 mb-6">
        <button
          onClick={() => navigate('/orders-new')}
          className="p-2 hover:bg-grey-input rounded-lg transition mr-2"
        >
          <ArrowLeft size={24} />
        </button>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-sans font-bold">
            № {order.orderNumber || order.order_number}
          </h1>
          <button
            onClick={() => copyToClipboard(order.orderNumber || order.order_number)}
            className="p-1 hover:bg-grey-input rounded transition"
            title="Скопировать номер"
          >
            {copiedId === (order.orderNumber || order.order_number) ? (
              <CheckCircle size={16} className="text-green-600" />
            ) : (
              <Copy size={16} className="text-grey-placeholder" />
            )}
          </button>
        </div>
        <div className="ml-auto">
          <Badge status={getStatusForBadge(order.status)}>
            {order.statusLabel || order.status}
          </Badge>
        </div>
      </div>

      {/* Quick Action Buttons - Short Links */}
      {order?.raw?.urls && (
        <div className="px-4 mb-4 flex flex-col gap-2">
          {/* Send to Customer */}
          {order.raw.urls.customer && order.sender_phone && (
            <button
              onClick={() => {
                const phone = order.sender_phone.replace(/[^0-9]/g, '');
                const text = encodeURIComponent(
                  `Здравствуйте! Вот ссылка для отслеживания вашего заказа #${order.orderNumber}:\n\n${order.raw.urls.customer}`
                );
                window.open(`https://wa.me/${phone}?text=${text}`, '_blank');
              }}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition font-sans text-sm"
            >
              <span>📤</span>
              <span>Отправить клиенту (заказчику)</span>
            </button>
          )}

          {/* Remind about Payment */}
          {order.raw.urls.pay && !order.is_paid && order.sender_phone && (
            <button
              onClick={() => {
                const phone = order.sender_phone.replace(/[^0-9]/g, '');
                const text = encodeURIComponent(
                  `Здравствуйте! Напоминаем об оплате заказа #${order.orderNumber}.\n\nОплатить через Kaspi Pay:\n${order.raw.urls.pay}`
                );
                window.open(`https://wa.me/${phone}?text=${text}`, '_blank');
              }}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-orange-50 hover:bg-orange-100 text-orange-700 rounded-lg transition font-sans text-sm"
            >
              <span>💳</span>
              <span>Напомнить об оплате</span>
            </button>
          )}
        </div>
      )}

      {/* Shop Badge */}
      {order.raw?.shopId && (
        <div className="px-4 mb-4">
          <div className="shop-badge inline-block px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg">
            <span className="text-sm font-sans text-blue-700">
              🏪 Магазин: {order.raw.shopId === '17008' ? 'Cvety.kz' : `ID ${order.raw.shopId}`}
            </span>
          </div>
        </div>
      )}

      {/* Photo Upload Section */}
      <PhotoUploadSection
        imageUrl={uploadedPhoto || order.assembled_photo}
        onUpload={handlePhotoUpload}
        label="Фото до доставки"
        isLoading={uploadingPhoto}
      />

      {/* Order Info */}
      <div className="px-4 mb-6 space-y-4">
        <div>
          <p className="text-sm text-grey-placeholder font-sans">Создан</p>
          <p className="text-base font-sans font-bold">{order.createdAt}</p>
          <p className="text-sm text-grey-placeholder font-sans">{order.createdAtDetailed}</p>
        </div>

        <div className="divider pt-4">
          <p className="text-sm text-grey-placeholder mb-1 font-sans">Сумма</p>
          <p className="text-2xl font-sans font-bold">
            {order.total}
          </p>
        </div>
      </div>

      {/* Items */}
      {order.items && order.items.length > 0 && (
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-4">Товары</h2>
          <div className="space-y-3">
            {order.items.map((item, index) => {
              const isExpanded = expandedItems.has(item.id);
              const toggleExpanded = () => {
                const newExpanded = new Set(expandedItems);
                if (isExpanded) {
                  newExpanded.delete(item.id);
                } else {
                  newExpanded.add(item.id);
                }
                setExpandedItems(newExpanded);
              };

              return (
                <div key={item.id || index} className="card p-3">
                  <div className="flex gap-3 items-start">
                    {item.image && (
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-12 h-12 object-cover rounded-full flex-shrink-0"
                      />
                    )}
                    <div className="flex-1">
                      <p className="font-sans font-bold text-sm">{item.name}</p>
                      <p className="text-xs text-grey-placeholder font-sans mt-1">Количество: {item.quantity}</p>
                      <p className="text-sm font-sans font-bold text-purple-primary mt-1">
                        {item.price}
                      </p>
                    </div>
                  </div>

                  {item.composition && item.composition.length > 0 && (
                    <div className="mt-3 pt-3 divider">
                      <button
                        onClick={toggleExpanded}
                        className="text-purple-primary font-sans text-xs hover:text-purple-hover transition"
                      >
                        {isExpanded ? 'Скрыть' : 'Состав'}
                      </button>

                      {isExpanded && (
                        <ul className="mt-2 space-y-1 text-xs font-sans text-grey-placeholder">
                          {item.composition.map((comp, idx) => (
                            <li key={idx} className="flex justify-between">
                              <span>{comp.name}</span>
                              <span>{comp.quantity} шт.</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Открытка - Figma Design */}
      {order.postcard_text && (
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-2">Открытка</h2>
          <p className="font-sans text-sm whitespace-pre-wrap">{decodeUnicodeEscapes(order.postcard_text)}</p>
        </div>
      )}

      {/* Послезавтрашняя - Figma Design */}
      {order.comment && (
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-2">Послезавтрашняя</h2>
          <p className="font-sans text-sm whitespace-pre-wrap">{order.comment}</p>
        </div>
      )}

      {/* Доставка - Figma Design Structure */}
      <div className="px-4 mb-6">
        <h2 className="text-lg font-sans font-bold mb-4">Доставка</h2>
        <div className="space-y-4">
          {/* Место */}
          {order.delivery_address && (
            <div>
              <p className="text-sm text-grey-placeholder font-sans mb-1">Место</p>
              <p className="font-sans">{order.delivery_address}</p>

              {/* Enhanced Ask Address Section */}
              {(order.raw?.askAddress || order.ask_address || order.raw?.ask_address) && (
                <div className="mt-3 p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl">⚠️</span>
                    <div>
                      <p className="font-sans font-bold text-yellow-800 text-sm">
                        Требуется уточнить адрес доставки
                      </p>
                      <p className="text-xs text-yellow-700 mt-1">
                        Клиент не указал точный адрес. Необходимо связаться с получателем.
                      </p>
                    </div>
                  </div>

                  {order.recipient?.phone ? (
                    <button
                      onClick={() => {
                        const phone = order.recipient.phone.replace(/[^0-9]/g, '');
                        const recipientUrl = order.raw?.raw?.urls?.recipient || order.raw?.urls?.recipient || '';
                        const statusUrl = order.raw?.raw?.urls?.status || order.raw?.urls?.status || '';
                        const trackingUrl = recipientUrl || statusUrl;
                        const text = encodeURIComponent(
                          `Здравствуйте! Уточните, пожалуйста, адрес доставки для заказа #${order.orderNumber || order.order_number}.${trackingUrl ? '\n\nСсылка для отслеживания: ' + trackingUrl : ''}`
                        );
                        window.open(`https://wa.me/${phone}?text=${text}`, '_blank');
                      }}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition font-sans text-sm font-medium"
                    >
                      <span>📱</span>
                      <span>Уточнить адрес у получателя через WhatsApp</span>
                    </button>
                  ) : (
                    <p className="text-sm text-yellow-700">
                      ⚠️ Телефон получателя не указан. Невозможно отправить запрос.
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Дата и время доставки */}
          {(order.delivery_date || order.delivery_time) && (
            <div className="divider pt-4">
              <p className="text-sm text-grey-placeholder font-sans mb-1">Доставка</p>
              <p className="font-sans">{formatDeliveryDateTime(order.delivery_date_raw || order.delivery_date, order.delivery_time)}</p>
            </div>
          )}
        </div>
      </div>

      {/* Получатель */}
      {(order.recipient_name || order.recipient_phone) && (
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-2">Получатель</h2>
          {order.recipient_name && (
            <p className="font-sans font-bold">{order.recipient_name}</p>
          )}
          {order.recipient_phone && (
            <div className="flex items-center gap-2 mt-1">
              <a
                href={`tel:${order.recipient_phone}`}
                className="text-purple-primary font-sans hover:text-purple-hover transition"
              >
                {order.recipient_phone}
              </a>
              <WhatsAppIcon phone={order.recipient_phone} size={18} />
            </div>
          )}
        </div>
      )}

      {/* Отправитель - Figma Design */}
      {(order.sender_name || order.sender_phone) && (
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-2">Отправитель</h2>
          {order.sender_name && (
            <p className="font-sans font-bold">{order.sender_name}</p>
          )}
          {order.sender_phone && (
            <div className="flex items-center gap-2 mt-1">
              <a
                href={`tel:${order.sender_phone}`}
                className="text-purple-primary font-sans hover:text-purple-hover transition"
              >
                {order.sender_phone}
              </a>
              <WhatsAppIcon phone={order.sender_phone} size={18} />
            </div>
          )}
          {order.sender_email && (
            <p className="text-grey-placeholder font-sans text-sm mt-1">{order.sender_email}</p>
          )}
        </div>
      )}

      {/* Оплата - Figma Design */}
      <div className="px-4 mb-6">
        <h2 className="text-lg font-sans font-bold mb-4">Оплата</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-grey-placeholder font-sans">Статус оплаты</span>
              {/* Using Design System Badge for payment status */}
              <Badge status={order.is_paid ? 'paid' : 'new'}>
                {order.is_paid ? 'Оплачен' : 'Не оплачен'}
              </Badge>
            </div>

            {order.payment_method && (
              <div className="divider pt-4">
                <p className="text-sm text-grey-placeholder font-sans">Способ оплаты</p>
                <p className="font-sans font-bold">{order.payment_method}</p>
              </div>
            )}

            {order.delivery_price > 0 && (
              <div className="divider pt-4">
                <p className="text-sm text-grey-placeholder font-sans">Стоимость доставки</p>
                <p className="font-sans font-bold">
                  {order.currency === 'USD' ? '$' : ''}
                  {order.delivery_price.toLocaleString('ru-RU', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                  })}
                  {order.currency === 'KZT' ? ' ₸' : ''}
                  {order.currency === 'EUR' ? ' €' : ''}
                </p>
              </div>
            )}

            {order.tracking_url && (
              <div className="divider pt-4">
                <p className="text-sm text-grey-placeholder font-sans">Ссылка на отслеживание</p>
                <button
                  onClick={() => copyToClipboard(order.tracking_url)}
                  className="flex items-center gap-2 text-purple-primary hover:text-purple-hover text-sm font-medium font-sans"
                >
                  {copiedId === order.tracking_url ? (
                    <>
                      <CheckCircle size={16} />
                      Скопирована
                    </>
                  ) : (
                    <>
                      <Copy size={16} />
                      Скопировать ссылку
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Photos */}
        {(order.assembled_photo || order.recipient_photo) && (
          <div className="px-4 mb-6">
            <h2 className="text-lg font-sans font-bold mb-4">Фотографии</h2>
            <div className="grid grid-cols-2 gap-4">
              {order.assembled_photo && (
                <div
                  onClick={() => setPhotoModal({
                    isOpen: true,
                    imageUrl: order.assembled_photo,
                    imageAlt: 'Собранный букет'
                  })}
                  className="cursor-pointer"
                >
                  <img
                    src={order.assembled_photo}
                    alt="Собранный букет"
                    className="w-full h-40 object-cover rounded-lg hover:opacity-80 transition"
                  />
                  <p className="text-sm text-grey-placeholder font-sans mt-2">Собранный букет</p>
                </div>
              )}

              {order.recipient_photo && (
                <div
                  onClick={() => setPhotoModal({
                    isOpen: true,
                    imageUrl: order.recipient_photo,
                    imageAlt: 'Фото получателя'
                  })}
                  className="cursor-pointer"
                >
                  <img
                    src={order.recipient_photo}
                    alt="Фото получателя"
                    className="w-full h-40 object-cover rounded-lg hover:opacity-80 transition"
                  />
                  <p className="text-sm text-grey-placeholder font-sans mt-2">Фото получателя</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Status Execution */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-4">Ответственный</h2>
          <div className="space-y-3">
            <DropdownField
              label="Ответственный"
              value={executorResponsible || ''}
              options={responsibleOptions}
              onChange={async (value) => {
                setExecutorResponsible(value);
                try {
                  setUpdating(true);
                  await ordersAPI.assignExecutors(orderId, {
                    responsible_id: value ? parseInt(value) : null
                  });
                  console.log('✅ Responsible assigned successfully');
                } catch (err) {
                  console.error('❌ Error assigning responsible:', err);
                  showError('Не удалось назначить ответственного');
                  setExecutorResponsible(order.raw?.responsibleId?.toString() || '');
                } finally {
                  setUpdating(false);
                }
              }}
              showBorder={false}
              disabled={updating}
            />
          </div>
        </div>

        {/* История - Figma Design with Expandable */}
        <div className="px-4 mb-6">
          <button
            onClick={() => setHistoryExpanded(!historyExpanded)}
            className="flex items-center justify-between w-full text-left"
          >
            <h2 className="text-lg font-sans font-bold">История</h2>
            <ChevronDown
              size={20}
              className={`text-grey-placeholder transition-transform ${historyExpanded ? 'rotate-180' : ''}`}
            />
          </button>

          {historyExpanded && order.history && order.history.length > 0 && (
            <div className="mt-4">
              <StatusTimeline events={order.history} />
            </div>
          )}

          {historyExpanded && (!order.history || order.history.length === 0) && (
            <div className="mt-4">
              <p className="text-sm text-grey-placeholder font-sans">История пока пуста</p>
            </div>
          )}
        </div>

        {/* Action Buttons - Using Design System Buttons */}
        <div className="px-4 mb-6 space-y-3">
          <Button
            variant="primary"
            size="lg"
            onClick={() => updateStatus(order.status === 'PAID' ? 'NEW' : 'PAID')}
            disabled={updating}
            className="w-full"
          >
            {order.is_paid ? 'ОПЛАЧЕНО' : 'ОПЛАЧЕН'}
          </Button>

          <Button
            variant="secondary"
            size="lg"
            onClick={() => navigate(`/orders/${orderId}/edit`)}
            className="w-full"
          >
            РЕДАКТИРОВАТЬ
          </Button>

          <Button
            variant="secondary"
            size="lg"
            onClick={() => {
              if (confirm('Вы уверены, что хотите удалить этот заказ?')) {
                ordersAPI.cancelOrder(orderId, 'Удалено пользователем').then(() => {
                  showSuccess('Заказ удален');
                  navigate('/orders-new');
                }).catch(err => {
                  showError(err.message || 'Ошибка при удалении');
                });
              }
            }}
            className="w-full bg-red-500 hover:bg-red-600 text-white border-red-500"
          >
            УДАЛИТЬ
          </Button>
        </div>

        {/* Bottom spacing */}
        <div className="h-4" />

      {/* Photo Modal */}
      <ImageModal
        isOpen={photoModal.isOpen}
        imageUrl={photoModal.imageUrl}
        imageAlt={photoModal.imageAlt}
        onClose={() => setPhotoModal({ isOpen: false, imageUrl: null, imageAlt: '' })}
      />
    </div>
  );
}

export default OrderDetail;
