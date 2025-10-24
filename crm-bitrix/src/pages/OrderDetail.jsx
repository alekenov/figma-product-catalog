import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import PriceFormatter from '../components/PriceFormatter';
import ImageModal from '../components/ImageModal';
import StatusTimeline from '../components/StatusTimeline';
import PhotoUploadSection from '../components/PhotoUploadSection';
import DropdownField from '../components/DropdownField';
import WhatsAppIcon from '../components/WhatsAppIcon';
import { useToast } from '../components/ToastProvider';
import { ArrowLeft, Copy, CheckCircle, Share2, Upload } from 'lucide-react';

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
  const [executorCourier, setExecutorCourier] = useState(null);

  // Expanded items state
  const [expandedItems, setExpandedItems] = useState(new Set());

  useEffect(() => {
    loadOrder();
  }, [orderId]);

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
      // For now, create a local preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedPhoto(e.target.result);
      };
      reader.readAsDataURL(file);
      showSuccess('Фото загружено');
    } catch (err) {
      showError('Ошибка при загрузке фото');
    } finally {
      setUploadingPhoto(false);
    }
  }

  function handleShareOrder() {
    const shareUrl = `${window.location.origin}/orders/${orderId}`;
    copyToClipboard(shareUrl);
    showSuccess('Ссылка скопирована в буфер обмена');
  }

  if (loading) return <LoadingSpinner message="Загрузка заказа..." />;

  if (error || !order) {
    return (
      <div className="figma-container bg-white flex items-center justify-center">
        <div className="p-6 text-center">
          <h2 className="text-lg font-sans font-bold text-red-600 mb-2">Ошибка</h2>
          <p className="text-gray-disabled mb-4">{error || 'Заказ не найден'}</p>
          <button
            onClick={() => navigate('/orders')}
            className="w-full bg-purple-primary hover:bg-purple-hover text-white py-2 rounded-lg transition font-sans"
          >
            Вернуться к заказам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-4 mb-6">
        <button
          onClick={() => navigate('/orders')}
          className="p-2 hover:bg-gray-input rounded-lg transition"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-xl font-sans font-bold flex-1 text-center">
          Заказ #{order.orderNumber || order.order_number}
        </h1>
        <button
          onClick={handleShareOrder}
          className="p-2 hover:bg-gray-input rounded-lg transition"
          title="Поделиться заказом"
        >
          <Share2 size={20} className="text-gray-placeholder" />
        </button>
      </div>

      {/* Status Badge */}
      <div className="px-4 mb-6 flex justify-end">
        <StatusBadge status={order.status} />
      </div>

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
          <p className="text-sm text-gray-placeholder font-sans">Создан</p>
          <p className="text-base font-sans font-bold">{order.createdAt}</p>
          <p className="text-sm text-gray-placeholder font-sans">{order.createdAtDetailed}</p>
        </div>

        <div className="border-t border-gray-border pt-4">
          <p className="text-sm text-gray-placeholder mb-1 font-sans">Сумма</p>
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
                <div key={item.id || index} className="border border-gray-border rounded-lg p-3">
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
                      <p className="text-xs text-gray-placeholder font-sans mt-1">Количество: {item.quantity}</p>
                      <p className="text-sm font-sans font-bold text-purple-primary mt-1">
                        {item.price}
                      </p>
                    </div>
                  </div>

                  {item.composition && item.composition.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-border">
                      <button
                        onClick={toggleExpanded}
                        className="text-purple-primary font-sans text-xs hover:text-purple-hover transition"
                      >
                        {isExpanded ? 'Скрыть' : 'Состав'}
                      </button>

                      {isExpanded && (
                        <ul className="mt-2 space-y-1 text-xs font-sans text-gray-placeholder">
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

      {/* Notification Button */}
      <div className="px-4 mb-6">
        <button className="w-full border-2 border-purple-primary text-purple-primary font-sans py-2 rounded-lg hover:bg-purple-primary hover:text-white transition">
          Оповестить о замене цветка
        </button>
      </div>

      {/* Customer & Recipient */}
      <div className="px-4 mb-6 space-y-4">
          {(order.sender_name || order.sender_phone) && (
            <div>
              <p className="text-sm text-gray-placeholder font-sans mb-2">Заказчик</p>
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
                <p className="text-gray-placeholder font-sans text-sm mt-1">{order.sender_email}</p>
              )}
            </div>
          )}

          {(order.recipient_name || order.recipient_phone) && (
            <div className="border-t border-gray-border pt-4">
              <p className="text-sm text-gray-placeholder font-sans mb-2">Получатель</p>
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

          {order.delivery_address && (
            <div className="border-t border-gray-border pt-4">
              <p className="text-sm text-gray-placeholder font-sans mb-1">Адрес доставки</p>
              <p className="font-sans">{order.delivery_address}</p>
            </div>
          )}

          {order.delivery_time && (
            <div className="border-t border-gray-border pt-4">
              <p className="text-sm text-gray-placeholder font-sans mb-1">Время доставки</p>
              <p className="font-sans">{order.delivery_time}</p>
            </div>
          )}
        </div>

        {/* Postcard & Comments */}
        {(order.postcard_text || order.comment) && (
          <div className="px-4 mb-6 space-y-4">
            {order.postcard_text && (
              <div>
                <p className="text-sm text-gray-placeholder font-sans mb-2">Текст открытки</p>
                <p className="font-sans whitespace-pre-wrap">{order.postcard_text}</p>
              </div>
            )}

            {order.comment && (
              <div className={order.postcard_text ? 'border-t border-gray-border pt-4' : ''}>
                <p className="text-sm text-gray-placeholder font-sans mb-2">Комментарий к заказу</p>
                <p className="font-sans whitespace-pre-wrap">{order.comment}</p>
              </div>
            )}
          </div>
        )}

        {/* Payment & Delivery */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-4">Оплата и доставка</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-placeholder font-sans">Статус оплаты</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                order.is_paid
                  ? 'bg-status-green text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {order.is_paid ? 'Оплачен' : 'Не оплачен'}
              </span>
            </div>

            {order.payment_method && (
              <div className="border-t border-gray-border pt-4">
                <p className="text-sm text-gray-placeholder font-sans">Способ оплаты</p>
                <p className="font-sans font-bold">{order.payment_method}</p>
              </div>
            )}

            {order.delivery_price > 0 && (
              <div className="border-t border-gray-border pt-4">
                <p className="text-sm text-gray-placeholder font-sans">Стоимость доставки</p>
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

            {order.delivery_date && (
              <div className="border-t border-gray-border pt-4">
                <p className="text-sm text-gray-placeholder font-sans">Дата доставки</p>
                <p className="font-sans font-bold">
                  {order.delivery_date}
                </p>
              </div>
            )}

            {order.tracking_url && (
              <div className="border-t border-gray-border pt-4">
                <p className="text-sm text-gray-placeholder font-sans">Ссылка на отслеживание</p>
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

        {/* Executors */}
        {order.executors && order.executors.length > 0 && (
          <div className="px-4 mb-6">
            <h2 className="text-lg font-sans font-bold mb-4">Исполнители</h2>
            <div className="space-y-4">
              {order.executors.map((executor, index) => (
                <div key={executor.id || index} className={index > 0 ? 'border-t border-gray-border pt-4' : ''}>
                  <p className="text-sm text-gray-placeholder font-sans mb-1">
                    {executor.role === 'florist' ? 'Флорист' :
                     executor.role === 'courier' ? 'Курьер' :
                     executor.role === 'manager' ? 'Менеджер' : 'Исполнитель'}
                  </p>
                  <div className="flex items-center gap-2">
                    <p className="font-sans font-bold">{executor.name || 'Не указан'}</p>
                    {executor.phone && (
                      <p className="text-sm text-gray-placeholder font-sans">{executor.phone}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

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
                  <p className="text-sm text-gray-placeholder font-sans mt-2">Собранный букет</p>
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
                  <p className="text-sm text-gray-placeholder font-sans mt-2">Фото получателя</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Status Execution */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-sans font-bold mb-4">Статус выполнения</h2>
          <div className="space-y-3">
            <DropdownField
              label="Статус"
              value={executorStatus || order.status}
              options={STATUS_OPTIONS}
              onChange={setExecutorStatus}
              showBorder={false}
            />
            <DropdownField
              label="Ответственный"
              value={executorResponsible || ''}
              options={[
                { value: 'florist_1', label: 'Флорист 1' },
                { value: 'florist_2', label: 'Флорист 2' },
                { value: 'manager_1', label: 'Менеджер 1' }
              ]}
              onChange={setExecutorResponsible}
              showBorder={false}
            />
            <DropdownField
              label="Курьер"
              value={executorCourier || ''}
              options={[
                { value: 'courier_1', label: 'Курьер 1' },
                { value: 'courier_2', label: 'Курьер 2' },
                { value: 'courier_3', label: 'Курьер 3' }
              ]}
              onChange={setExecutorCourier}
              showBorder={false}
            />
          </div>
        </div>

        {/* Order History */}
        {order.history && order.history.length > 0 && (
          <div className="px-4 mb-6">
            <h2 className="text-lg font-sans font-bold mb-4">История заказа</h2>
            <StatusTimeline events={order.history} />
          </div>
        )}

        {/* Action Buttons */}
        <div className="px-4 mb-6 space-y-3">
          <button
            onClick={() => updateStatus(order.status === 'PAID' ? 'NEW' : 'PAID')}
            disabled={updating}
            className="w-full bg-purple-primary hover:bg-purple-hover text-white font-sans font-bold py-3 rounded-lg transition disabled:opacity-50"
          >
            {order.is_paid ? 'ОПЛАЧЕНО' : 'ОПЛАЧЕН'}
          </button>
          <button
            onClick={() => navigate(`/orders/${orderId}/edit`)}
            className="w-full border-2 border-purple-primary text-purple-primary font-sans font-bold py-3 rounded-lg hover:bg-purple-primary hover:text-white transition"
          >
            РЕДАКТИРОВАТЬ
          </button>
          <button
            onClick={() => {
              if (confirm('Вы уверены, что хотите удалить этот заказ?')) {
                ordersAPI.cancelOrder(orderId, 'Удалено пользователем').then(() => {
                  showSuccess('Заказ удален');
                  navigate('/orders');
                }).catch(err => {
                  showError(err.message || 'Ошибка при удалении');
                });
              }
            }}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-sans font-bold py-3 rounded-lg transition disabled:opacity-50"
          >
            УДАЛИТЬ
          </button>
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
