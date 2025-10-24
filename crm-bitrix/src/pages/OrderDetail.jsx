import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import PriceFormatter from '../components/PriceFormatter';
import ImageModal from '../components/ImageModal';
import StatusTimeline from '../components/StatusTimeline';
import { useToast } from '../components/ToastProvider';
import { ArrowLeft, Copy, CheckCircle } from 'lucide-react';

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

  if (loading) return <LoadingSpinner message="Загрузка заказа..." />;

  if (error || !order) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-lg font-semibold text-red-600 mb-2">Ошибка</h2>
          <p className="text-gray-700 mb-4">{error || 'Заказ не найден'}</p>
          <button
            onClick={() => navigate('/orders')}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition"
          >
            Вернуться к заказам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto p-4">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate('/orders')}
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            Заказ #{order.orderNumber || order.order_number}
          </h1>
        </div>

        {/* Order Info */}
        <div className="bg-white rounded-lg p-6 mb-6 space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">Создан</p>
              <p className="text-lg font-medium">{order.createdAt}</p>
              <p className="text-sm text-gray-400">{order.createdAtDetailed}</p>
            </div>
            <StatusBadge status={order.status} />
          </div>

          <div className="border-t pt-4">
            <p className="text-sm text-gray-500 mb-1">Сумма</p>
            <p className="text-2xl font-bold text-gray-900">
              {order.total}
            </p>
          </div>
        </div>

        {/* Items */}
        {order.items && order.items.length > 0 && (
          <div className="bg-white rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Товары</h2>
            <div className="space-y-4">
              {order.items.map((item, index) => (
                <div key={item.id || index} className="flex gap-4 items-start">
                  {item.image && (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                  )}
                  <div className="flex-1">
                    <p className="font-medium">{item.name}</p>
                    <p className="text-sm text-gray-500">Количество: {item.quantity}</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {item.price}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Customer & Recipient */}
        <div className="bg-white rounded-lg p-6 mb-6 space-y-4">
          {(order.sender_name || order.sender_phone) && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Заказчик</p>
              {order.sender_name && (
                <p className="font-medium">{order.sender_name}</p>
              )}
              {order.sender_phone && (
                <p className="text-gray-700">{order.sender_phone}</p>
              )}
              {order.sender_email && (
                <p className="text-gray-700 text-sm">{order.sender_email}</p>
              )}
            </div>
          )}

          {(order.recipient_name || order.recipient_phone) && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-2">Получатель</p>
              {order.recipient_name && (
                <p className="font-medium">{order.recipient_name}</p>
              )}
              {order.recipient_phone && (
                <p className="text-gray-700">{order.recipient_phone}</p>
              )}
            </div>
          )}

          {order.delivery_address && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Адрес доставки</p>
              <p className="text-lg">{order.delivery_address}</p>
            </div>
          )}

          {order.delivery_time && (
            <div className="border-t pt-4">
              <p className="text-sm text-gray-500 mb-1">Время доставки</p>
              <p className="text-lg">{order.delivery_time}</p>
            </div>
          )}
        </div>

        {/* Postcard & Comments */}
        {(order.postcard_text || order.comment) && (
          <div className="bg-white rounded-lg p-6 mb-6 space-y-4">
            {order.postcard_text && (
              <div>
                <p className="text-sm text-gray-500 mb-2">Текст открытки</p>
                <p className="text-gray-900 whitespace-pre-wrap">{order.postcard_text}</p>
              </div>
            )}

            {order.comment && (
              <div className={order.postcard_text ? 'border-t pt-4' : ''}>
                <p className="text-sm text-gray-500 mb-2">Комментарий к заказу</p>
                <p className="text-gray-900 whitespace-pre-wrap">{order.comment}</p>
              </div>
            )}
          </div>
        )}

        {/* Payment & Delivery */}
        <div className="bg-white rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Оплата и доставка</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Статус оплаты</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                order.is_paid
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {order.is_paid ? 'Оплачен' : 'Не оплачен'}
              </span>
            </div>

            {order.payment_method && (
              <div className="border-t pt-4">
                <p className="text-sm text-gray-500">Способ оплаты</p>
                <p className="text-lg font-medium">{order.payment_method}</p>
              </div>
            )}

            {order.delivery_price > 0 && (
              <div className="border-t pt-4">
                <p className="text-sm text-gray-500">Стоимость доставки</p>
                <p className="text-lg font-medium">
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
              <div className="border-t pt-4">
                <p className="text-sm text-gray-500">Дата доставки</p>
                <p className="text-lg font-medium">
                  {order.delivery_date}
                </p>
              </div>
            )}

            {order.tracking_url && (
              <div className="border-t pt-4">
                <p className="text-sm text-gray-500">Ссылка на отслеживание</p>
                <button
                  onClick={() => copyToClipboard(order.tracking_url)}
                  className="flex items-center gap-2 text-purple-600 hover:text-purple-700 text-sm font-medium"
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
          <div className="bg-white rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Исполнители</h2>
            <div className="space-y-4">
              {order.executors.map((executor, index) => (
                <div key={executor.id || index} className={index > 0 ? 'border-t pt-4' : ''}>
                  <p className="text-sm text-gray-500 mb-1">
                    {executor.role === 'florist' ? 'Флорист' :
                     executor.role === 'courier' ? 'Курьер' :
                     executor.role === 'manager' ? 'Менеджер' : 'Исполнитель'}
                  </p>
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-medium">{executor.name || 'Не указан'}</p>
                    {executor.phone && (
                      <p className="text-sm text-gray-600">{executor.phone}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Photos */}
        {(order.assembled_photo || order.recipient_photo) && (
          <div className="bg-white rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Фотографии</h2>
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
                  <p className="text-sm text-gray-600 mt-2">Собранный букет</p>
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
                  <p className="text-sm text-gray-600 mt-2">Фото получателя</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Order History */}
        {order.history && order.history.length > 0 && (
          <div className="bg-white rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">История заказа</h2>
            <StatusTimeline events={order.history} />
          </div>
        )}

        {/* Status Update */}
        <div className="bg-white rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Изменить статус</h2>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {STATUS_OPTIONS.map(option => (
              <button
                key={option.value}
                onClick={() => updateStatus(option.value)}
                disabled={updating || option.value === order.status}
                className={`p-3 rounded-lg font-medium transition ${
                  option.value === order.status
                    ? 'bg-purple-600 text-white cursor-default'
                    : 'bg-gray-100 hover:bg-gray-200 disabled:opacity-50'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

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
