import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import StatusBadge from './components/StatusBadge';
import InfoRow from './components/InfoRow';
import SectionHeader from './components/SectionHeader';
import DateTimeSelectorAdmin from './components/DateTimeSelectorAdmin';
import { useToast } from './components/ToastProvider';
import { ordersAPI, formatOrderForDisplay } from './services/api';
import './App.css';

// Изображения товаров из Figma
const imgRectangle = "https://s3-alpha-sig.figma.com/img/9407/eaaf/09bc0cd0735147c984706db31a71bf86?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=ZcUeI1p2PVhMbX3i9N-PWBbsiy8bea6nrc4JfagIE1NVkzuPa~-NYksSPPYlSLvgQRnAu2roiYrlV8szvC8sVZhCTEjCWqHtgqxxpNfGzbrJMOP1SOiaG4EUtRH0kLIuxYeGVnG29c2UPbvOxzMbZ0LTclLvBcDbZ9IFeM53ocnSUXiTS-Pr0VfzE6uIZHegW8wdWALH8Xkvxagnw~D6YwxO~DHzYoUv37ryhBX37hfC2NVEBYsMoBWCEUfqW-EI8zu-E9lKQ9S0LuDo~U7pBQGvm6OshQfOo4yA0HjVT1GCJ8Ah~h~5tZOgfFKzzBRbXmzXvBVOQ7JI~jbVIdhDGQ__";
const imgRectangle1 = "https://s3-alpha-sig.figma.com/img/6ac5/fd2f/59330fdd9f8b4e0196fdeb1e357e80e3?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=oFyKh7nrZj~6-XDIPvg4k4uWu2KIRgvi~q9rL5S~HsDdAw9qbJJrGCtWuPobF6VLKi5TGJruMMQ~oqxNlyQnN-jrw8zlRdj2kHv8bPBYB61PP9mdF~SiI9fpxinJYp~In5v07JJKjN-KwMIln3kBvyDBPtXsclu8ElbRf2JQhDmqViGf5ng8e9RrXH4FCVVtt08rJm1a0xQqL1HwkoecuYmFdQuOHaYONGwG1oqyak9W4ySoM50QjxT1cigeQPtBULOURGOz~iAVL3fHDYNPckDtlWImq7GUV1zic7oBTwVGYPhll6ONfPiEzKumxKo3m9xFJExYyEvxBP4FNe5b3A__";
const imgRectangle2 = "https://s3-alpha-sig.figma.com/img/d4d9/54b8/cb8a5c7b807046d49f7e09b0f80ca5d3?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=jlb4b08XVwrod-dsiaCfPnduD7EFsfgOucqFRo3TNsE758kJ7wc2ypErXx~p1KeLb1QyXSOTDgLIpHtPaaJQaeuovLPxDvu3usc3VUmBOQgLoVDqgAIE8jFr9Dy-AeVBwA68rRLi~aA9fU3CvrukN6v2Pe4KLW-TylZ3s-ETvs5J53p8EPK-rDOja6gd9FN8Q4duU0T6wjVKIzYjoBBuCTm7UA-KSCdwYEqICpFMEzIIMQ-hSdjmhXkyMDZMi04s-R7YQTKtOemKmiGmyrkM9YfzsrPv88KL9QZ1ik5iFBTGKNWOCxYFueW01GS9bMzgYN~gbmRKJuCpcUV2xMp37A__";
const imgRectangle3 = "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__";

const OrderDetail = () => {
  const navigate = useNavigate();
  const { orderId } = useParams();
  const { showSuccess } = useToast();
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recipientInfo, setRecipientInfo] = useState(null);
  const [isStatusDropdownOpen, setIsStatusDropdownOpen] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [orderHistory, setOrderHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Photo upload state
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false);
  const photoFileInputRef = React.useRef(null);

  // Order editing state
  const [isEditingOrder, setIsEditingOrder] = useState(false);
  const [editedFields, setEditedFields] = useState({
    delivery_address: '',
    delivery_date: '',
    delivery_notes: ''
  });

  // Date/time selector state for new UI
  const [selectedDate, setSelectedDate] = useState(''); // 'today' | 'tomorrow' | ''
  const [selectedTime, setSelectedTime] = useState(''); // '09:00-11:00' | etc.

  // Team assignment state
  const [teamMembers, setTeamMembers] = useState([]);
  const [loadingTeam, setLoadingTeam] = useState(false);
  const [isResponsibleDropdownOpen, setIsResponsibleDropdownOpen] = useState(false);
  const [isCourierDropdownOpen, setIsCourierDropdownOpen] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  // Kaspi refund state
  const [refundAmount, setRefundAmount] = useState('');
  const [isRefunding, setIsRefunding] = useState(false);

  // Get user role from localStorage
  const userRole = JSON.parse(localStorage.getItem('user') || '{}').role;

  const handleBack = () => {
    navigate('/orders');
  };

  // All available order statuses
  const availableStatuses = [
    { id: 'new', label: 'Новый' },
    { id: 'paid', label: 'Оплачен' },
    { id: 'accepted', label: 'Принят' },
    { id: 'assembled', label: 'Собран' },
    { id: 'in_delivery', label: 'В доставке' },
    { id: 'delivered', label: 'Доставлен' },
    { id: 'cancelled', label: 'Отменен' }
  ];

  // Handle status change
  const handleStatusChange = async (newStatus) => {
    if (!orderData || isUpdatingStatus) return;

    try {
      setIsUpdatingStatus(true);

      // Call API to update status
      await ordersAPI.updateOrderStatus(orderId, newStatus);

      // Update local state
      const newStatusLabel = availableStatuses.find(s => s.id === newStatus)?.label || newStatus;
      setOrderData({
        ...orderData,
        status: newStatus,
        statusLabel: newStatusLabel
      });

      // Close dropdown
      setIsStatusDropdownOpen(false);

      // Show success message
      showSuccess(`Статус заказа изменен на "${newStatusLabel}"`);
    } catch (err) {
      console.error('Failed to update order status:', err);
      alert('Не удалось изменить статус заказа');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  // Fetch order history
  const fetchOrderHistory = async () => {
    try {
      setLoadingHistory(true);
      const response = await fetch(`http://localhost:8014/api/v1/orders/${orderId}/history`);

      if (!response.ok) {
        throw new Error('Failed to fetch order history');
      }

      const history = await response.json();
      setOrderHistory(history);
    } catch (err) {
      console.error('Failed to load order history:', err);
      // Don't show error to user for history - just log it
    } finally {
      setLoadingHistory(false);
    }
  };

  // Format field names in Russian
  const formatFieldName = (fieldName) => {
    const fieldNames = {
      'recipient_name': 'Имя получателя',
      'recipient_phone': 'Телефон получателя',
      'sender_phone': 'Телефон отправителя',
      'delivery_address': 'Адрес доставки',
      'pickup_address': 'Адрес самовывоза',
      'delivery_date': 'Дата доставки',
      'delivery_notes': 'Заметки к доставке',
      'status': 'Статус',
      'customerName': 'Имя заказчика',
      'phone': 'Телефон',
      'customer_email': 'Email',
      'notes': 'Комментарий',
      'scheduled_time': 'Время доставки',
      'payment_method': 'Способ оплаты',
      'order_comment': 'Комментарий к заказу',
      'assigned_to': 'Ответственный',
      'courier': 'Курьер'
    };
    return fieldNames[fieldName] || fieldName;
  };

  // Fetch team members for assignment
  const fetchTeamMembers = async () => {
    try {
      setLoadingTeam(true);
      const token = localStorage.getItem('auth_token');

      const response = await fetch('http://localhost:8014/api/v1/auth/users', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch team members');
      }

      const users = await response.json();
      setTeamMembers(users);
    } catch (err) {
      console.error('Failed to load team members:', err);
      // Don't show error to user - just log it
    } finally {
      setLoadingTeam(false);
    }
  };

  // Handle assign responsible
  const handleAssignResponsible = async (userId) => {
    if (!orderData || isAssigning) return;

    try {
      setIsAssigning(true);
      const token = localStorage.getItem('auth_token');

      const response = await fetch(`http://localhost:8014/api/v1/orders/${orderId}/assign-responsible`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to assign responsible');
      }

      // Refresh order data
      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);
      setOrderData(formattedOrder);

      // Refresh history
      fetchOrderHistory();

      // Close dropdown
      setIsResponsibleDropdownOpen(false);

      const assignedUser = teamMembers.find(u => u.id === userId);
      showSuccess(`Ответственный назначен: ${assignedUser?.name || 'Пользователь'}`);
    } catch (err) {
      console.error('Failed to assign responsible:', err);
      alert('Не удалось назначить ответственного: ' + err.message);
    } finally {
      setIsAssigning(false);
    }
  };

  // Handle assign courier
  const handleAssignCourier = async (userId) => {
    if (!orderData || isAssigning) return;

    try {
      setIsAssigning(true);
      const token = localStorage.getItem('auth_token');

      const response = await fetch(`http://localhost:8014/api/v1/orders/${orderId}/assign-courier`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to assign courier');
      }

      // Refresh order data
      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);
      setOrderData(formattedOrder);

      // Refresh history
      fetchOrderHistory();

      // Close dropdown
      setIsCourierDropdownOpen(false);

      const assignedUser = teamMembers.find(u => u.id === userId);
      showSuccess(`Курьер назначен: ${assignedUser?.name || 'Пользователь'}`);
    } catch (err) {
      console.error('Failed to assign courier:', err);
      alert('Не удалось назначить курьера: ' + err.message);
    } finally {
      setIsAssigning(false);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const timeStr = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

    if (date.toDateString() === today.toDateString()) {
      return `Сегодня ${timeStr}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
      return `Вчера ${timeStr}`;
    } else {
      return date.toLocaleString('ru-RU', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  // Get next status in the order workflow
  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      'new': 'paid',
      'paid': 'accepted',
      'accepted': 'assembled',
      'assembled': 'in_delivery',
      'in_delivery': 'delivered',
      'delivered': null,
      'cancelled': null
    };
    return statusFlow[currentStatus] || null;
  };

  // Get button text for next status
  const getNextStatusButtonText = (currentStatus) => {
    const buttonTexts = {
      'new': 'ОПЛАЧЕН',
      'paid': 'ПРИНЯТЬ',
      'accepted': 'СОБРАН',
      'assembled': 'В ПУТИ',
      'in_delivery': 'ДОСТАВЛЕН'
    };
    return buttonTexts[currentStatus] || 'ОПЛАЧЕН';
  };

  // Handle next status button click
  const handleNextStatus = async () => {
    if (!orderData) return;
    const nextStatus = getNextStatus(orderData.status);
    if (nextStatus) {
      await handleStatusChange(nextStatus);
    }
  };

  // Handle cancel order
  const handleCancelOrder = async () => {
    if (!orderData || orderData.status === 'cancelled') return;

    if (window.confirm('Вы уверены, что хотите отменить заказ?')) {
      await handleStatusChange('cancelled');
    }
  };

  // Handle order editing
  const handleEditOrder = () => {
    if (!orderData) return;

    // Parse ISO datetime to date tab and time slot
    let dateTab = '';
    let timeSlot = '';

    if (orderData.delivery_date_raw) {
      const date = new Date(orderData.delivery_date_raw);
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      // Determine if today or tomorrow
      if (date.toDateString() === today.toDateString()) {
        dateTab = 'today';
      } else if (date.toDateString() === tomorrow.toDateString()) {
        dateTab = 'tomorrow';
      }

      // Extract time and find matching slot
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const timeStr = `${hours}:${minutes}`;

      // Time slots available
      const timeSlots = [
        '09:00-11:00', '11:00-13:00', '13:00-15:00',
        '15:00-17:00', '17:00-19:00', '19:00-21:00'
      ];

      // Find matching slot by start time
      const matchedSlot = timeSlots.find(slot => slot.startsWith(timeStr));
      if (matchedSlot) {
        timeSlot = matchedSlot;
      }
    }

    setSelectedDate(dateTab);
    setSelectedTime(timeSlot);

    setEditedFields({
      delivery_address: orderData.delivery_address || '',
      delivery_date: '', // We'll use selectedDate/selectedTime instead
      delivery_notes: orderData.delivery_notes || ''
    });
    setIsEditingOrder(true);
  };

  const handleSaveOrder = async () => {
    if (!orderData) return;

    try {
      setIsUpdatingStatus(true);

      // Prepare update data
      const updateData = {};

      if (editedFields.delivery_address !== orderData.delivery_address) {
        updateData.delivery_address = editedFields.delivery_address;
      }

      // Reconstruct ISO datetime from selectedDate and selectedTime
      if (selectedDate && selectedTime) {
        // Determine target date
        let targetDate = new Date();
        if (selectedDate === 'tomorrow') {
          targetDate.setDate(targetDate.getDate() + 1);
        }

        // Extract start time from slot (e.g., "09:00" from "09:00-11:00")
        const [startTime] = selectedTime.split('-');
        const [hours, minutes] = startTime.split(':');

        // Set time on target date
        targetDate.setHours(parseInt(hours, 10));
        targetDate.setMinutes(parseInt(minutes, 10));
        targetDate.setSeconds(0);
        targetDate.setMilliseconds(0);

        updateData.delivery_date = targetDate.toISOString();
      }

      if (editedFields.delivery_notes !== orderData.delivery_notes) {
        updateData.delivery_notes = editedFields.delivery_notes;
      }

      // Only update if there are changes
      if (Object.keys(updateData).length > 0) {
        await ordersAPI.updateOrder(orderId, updateData);

        // Refresh order data
        const rawOrder = await ordersAPI.getOrder(orderId);
        const formattedOrder = formatOrderForDisplay(rawOrder);
        setOrderData(formattedOrder);

        // Fetch updated history
        fetchOrderHistory();

        showSuccess('Заказ обновлён');
      }

      setIsEditingOrder(false);
    } catch (err) {
      console.error('Failed to update order:', err);
      alert('Не удалось обновить заказ: ' + err.message);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleCancelEditOrder = () => {
    setIsEditingOrder(false);
    setEditedFields({
      delivery_address: '',
      delivery_date: '',
      delivery_notes: ''
    });
    setSelectedDate('');
    setSelectedTime('');
  };

  // Photo upload handlers
  const handlePhotoClick = () => {
    if (photoFileInputRef.current) {
      photoFileInputRef.current.click();
    }
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
    if (file.size > 10 * 1024 * 1024) {
      alert('Файл слишком большой. Максимум 10MB');
      return;
    }

    try {
      setIsUploadingPhoto(true);

      // Upload photo
      const result = await ordersAPI.uploadOrderPhoto(orderId, file);

      // Refresh order data to get updated photo and status
      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);
      setOrderData(formattedOrder);

      showSuccess('Фото загружено успешно');
    } catch (err) {
      console.error('Failed to upload photo:', err);
      alert('Не удалось загрузить фото: ' + err.message);
    } finally {
      setIsUploadingPhoto(false);
      // Reset file input
      if (photoFileInputRef.current) {
        photoFileInputRef.current.value = '';
      }
    }
  };

  const handlePhotoDelete = async () => {
    if (!window.confirm('Удалить фото? Статус заказа вернется к "Принят".')) {
      return;
    }

    try {
      setIsUploadingPhoto(true);

      await ordersAPI.deleteOrderPhoto(orderId);

      // Refresh order data
      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);
      setOrderData(formattedOrder);

      showSuccess('Фото удалено успешно');
    } catch (err) {
      console.error('Failed to delete photo:', err);
      alert('Не удалось удалить фото: ' + err.message);
    } finally {
      setIsUploadingPhoto(false);
    }
  };

  // Fetch order data from API
  useEffect(() => {
    const fetchOrder = async () => {
      if (!orderId) {
        setError('Не указан ID заказа');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const rawOrder = await ordersAPI.getOrder(orderId);
        const formattedOrder = formatOrderForDisplay(rawOrder);
        setOrderData(formattedOrder);

        // Extract recipient info from notes if present
        if (formattedOrder.notes) {
          const recipientMatch = formattedOrder.notes.match(/Получатель: (.+?), тел: (.+?)(?:\n|$)/);
          if (recipientMatch) {
            setRecipientInfo({
              name: recipientMatch[1],
              phone: recipientMatch[2]
            });
          }
        }

        // Fetch order history
        fetchOrderHistory();

        // Fetch team members for assignment
        fetchTeamMembers();

        setError(null);
      } catch (err) {
        console.error('Failed to fetch order:', err);
        setError('Не удалось загрузить данные заказа');
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [orderId]);

  // Auto-fill refund amount when order data loads for Kaspi orders
  useEffect(() => {
    if (orderData?.payment_method === 'kaspi' &&
        orderData?.kaspi_payment_status === 'Processed' &&
        orderData?.totalRaw) {
      // Convert kopecks to tenge
      setRefundAmount(String(orderData.totalRaw / 100));
    }
  }, [orderData]);

  // Copy tracking link to clipboard
  const handleCopyTrackingLink = async () => {
    if (!orderData?.tracking_id) {
      alert('Tracking ID не найден');
      return;
    }

    // Construct tracking URL - in production this should use the actual domain
    const trackingUrl = `http://localhost:5180/status/${orderData.tracking_id}`;

    try {
      await navigator.clipboard.writeText(trackingUrl);
      showSuccess('Ссылка для отслеживания скопирована в буфер обмена');
    } catch (err) {
      console.error('Failed to copy tracking link:', err);
      alert('Не удалось скопировать ссылку');
    }
  };

  // Handle Kaspi refund
  const handleKaspiRefund = async () => {
    if (!orderData?.kaspi_payment_id || !refundAmount) return;

    const amount = parseFloat(refundAmount);
    const maxAmount = orderData.totalRaw / 100; // Convert kopecks to tenge

    // Validation
    if (isNaN(amount) || amount <= 0) {
      alert('Введите корректную сумму возврата');
      return;
    }

    if (amount > maxAmount) {
      alert(`Сумма возврата не может превышать ${maxAmount} ₸`);
      return;
    }

    // Confirmation
    if (!window.confirm(`Вернуть ${amount} ₸ клиенту через Kaspi Pay?`)) {
      return;
    }

    try {
      setIsRefunding(true);
      const token = localStorage.getItem('auth_token');

      const response = await fetch('http://localhost:8014/api/v1/kaspi/refund', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          external_id: orderData.kaspi_payment_id,
          amount: amount
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка возврата средств');
      }

      showSuccess(`Возврат ${amount} ₸ выполнен успешно`);
      setRefundAmount('');

      // Refresh order data
      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);
      setOrderData(formattedOrder);

    } catch (err) {
      console.error('Kaspi refund failed:', err);
      alert('Не удалось выполнить возврат: ' + err.message);
    } finally {
      setIsRefunding(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isStatusDropdownOpen && !event.target.closest('.relative')) {
        setIsStatusDropdownOpen(false);
      }
    };

    if (isStatusDropdownOpen) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [isStatusDropdownOpen]);

  // Loading state
  if (loading) {
    return (
      <div className="figma-container bg-white relative min-h-screen">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-placeholder">Загрузка заказа...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="figma-container bg-white relative min-h-screen">
        <div className="flex flex-col justify-center items-center h-64">
          <div className="text-red-500 mb-4">{error}</div>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-purple-primary text-white rounded"
          >
            Назад к заказам
          </button>
        </div>
      </div>
    );
  }

  // No data state
  if (!orderData) {
    return (
      <div className="figma-container bg-white relative min-h-screen">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-placeholder">Заказ не найден</div>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white relative min-h-screen">
      {/* Header */}
      <div className="bg-white h-[62px] relative">
        <div className="border-b border-gray-border"></div>

        {/* Back button */}
        <button
          onClick={handleBack}
          className="absolute left-4 top-[19px] w-6 h-6 flex items-center justify-center"
        >
          <svg className="w-6 h-6 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Order number */}
        <h1 className="absolute left-12 top-4 text-xl font-['Open_Sans'] font-normal leading-[30px]">
          {orderData.orderNumber}
        </h1>

        {/* Status badge */}
        <div className="absolute right-4 top-[18px]">
          <StatusBadge status={orderData.status} label={orderData.statusLabel} />
        </div>

        {/* Share button - Copy tracking link */}
        <button
          onClick={handleCopyTrackingLink}
          className="absolute right-16 top-[19px] w-6 h-6 hover:opacity-70 transition-opacity"
          title="Скопировать ссылку для клиента"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
        </button>
      </div>

      {/* Photo before delivery section - Interactive */}
      <input
        ref={photoFileInputRef}
        type="file"
        accept="image/*"
        onChange={handlePhotoSelect}
        className="hidden"
      />

      <div className="px-4 py-4">
        {/* Check if photo exists */}
        {orderData.photos && orderData.photos.length > 0 ? (
          /* Photo uploaded - show preview with actions */
          <div className="space-y-3">
            <div className="text-base font-['Open_Sans'] text-black">Фото до доставки</div>
            <div className="relative w-20 h-20 rounded-lg overflow-hidden">
              <img
                src={orderData.photos[0].url}
                alt="Фото до доставки"
                className="w-full h-full object-cover"
              />
            </div>

            {/* Client Feedback Display */}
            {orderData.photos[0].feedback && (
              <div className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <span className="text-xl">
                  {orderData.photos[0].feedback === 'like' ? '👍' : '👎'}
                </span>
                <div className="flex-1">
                  <div className="text-sm font-['Open_Sans'] font-semibold text-black">
                    {orderData.photos[0].feedback === 'like'
                      ? 'Клиенту понравился букет'
                      : 'Клиент оставил комментарий'}
                  </div>
                  {orderData.photos[0].comment && (
                    <div className="text-sm font-['Open_Sans'] text-gray-600 mt-1">
                      {orderData.photos[0].comment}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={handlePhotoClick}
                disabled={isUploadingPhoto}
                className="px-4 py-2 text-sm font-['Open_Sans'] text-purple-primary border border-purple-primary rounded hover:bg-purple-50 disabled:opacity-50"
              >
                Заменить
              </button>
              <button
                onClick={handlePhotoDelete}
                disabled={isUploadingPhoto}
                className="px-4 py-2 text-sm font-['Open_Sans'] text-red-600 border border-red-600 rounded hover:bg-red-50 disabled:opacity-50"
              >
                Удалить
              </button>
            </div>
          </div>
        ) : (
          /* No photo - clickable upload area */
          <div
            onClick={isUploadingPhoto ? undefined : handlePhotoClick}
            className={`flex items-center gap-3 ${isUploadingPhoto ? 'opacity-50' : 'cursor-pointer hover:bg-gray-50 transition-colors'} rounded-lg p-2 -m-2`}
          >
            <div className="w-12 h-12 bg-purple-light rounded-full flex items-center justify-center">
              {isUploadingPhoto ? (
                <svg className="animate-spin h-5 w-5 text-purple-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
            </div>
            <div className="flex-1">
              <div className="text-base font-['Open_Sans'] text-black">Фото до доставки</div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mt-1">
                {isUploadingPhoto ? 'Загрузка...' : 'Не добавлено'}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="border-b border-gray-border"></div>

      {/* Order items */}
      {orderData.items && orderData.items.length > 0 && (
        <div className="px-4 py-4">
          {orderData.items.map((item, index) => (
            <div key={index} className="flex items-start gap-3 mb-4">
              <div className="w-12 h-12 rounded-full overflow-hidden">
                <img src={imgRectangle3} alt="" className="w-full h-full object-cover" />
              </div>
              <div className="flex-1">
                <div className="text-base font-['Open_Sans'] text-black">{item.name}</div>
                <div className="text-sm font-['Open_Sans'] text-gray-disabled mt-1 leading-normal">
                  <div>Количество: {item.quantity} шт.</div>
                  {item.price && (
                    <div>Цена за единицу: {item.price}</div>
                  )}
                  {item.description && (
                    <div className="mt-1">Описание: {item.description}</div>
                  )}
                  {item.special_requests && (
                    <div className="mt-1">Пожелания: {item.special_requests}</div>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-base font-['Open_Sans'] text-black">{item.total}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Comment */}
      {orderData.notes && (
        <div className="px-4 pb-6">
          <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Комментарий</div>
          <div className="text-base font-['Open_Sans'] text-black leading-normal">
            {orderData.notes}
          </div>
        </div>
      )}

      {/* Delivery section */}
      <div className="px-4 pb-6">
        <SectionHeader title="Доставка" />

        <div className="space-y-4">
          {/* Данные получателя (если есть) */}
          {recipientInfo && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Получатель</div>
              <div className="text-base font-['Open_Sans'] text-black flex items-center gap-2">
                {recipientInfo.name}, <span className="text-purple-primary">{recipientInfo.phone}</span>
                <svg className="w-6 h-6 text-whatsapp" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.108"/>
                </svg>
              </div>
            </div>
          )}

          {/* Данные заказчика/отправителя */}
          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Заказчик</div>
            <div className="text-base font-['Open_Sans'] text-black flex items-center gap-2">
              {orderData.customerName}, <span className="text-purple-primary">{orderData.phone}</span>
              <svg className="w-6 h-6 text-whatsapp" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.108"/>
              </svg>
            </div>
          </div>

          {orderData.customer_email && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Email отправителя</div>
              <div className="text-base font-['Open_Sans'] text-purple-primary">{orderData.customer_email}</div>
            </div>
          )}

          {(orderData.delivery_address || isEditingOrder) && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Адрес доставки</div>
              {isEditingOrder ? (
                <input
                  type="text"
                  value={editedFields.delivery_address}
                  onChange={(e) => setEditedFields({ ...editedFields, delivery_address: e.target.value })}
                  placeholder="Введите адрес доставки"
                  className="w-full px-3 py-2 border border-gray-border rounded text-base font-['Open_Sans'] text-black focus:outline-none focus:ring-2 focus:ring-purple-primary"
                  disabled={isUpdatingStatus}
                />
              ) : (
                <div className="text-base font-['Open_Sans'] text-black">{orderData.delivery_address}</div>
              )}
            </div>
          )}

          {(orderData.delivery_date || isEditingOrder) && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Дата доставки</div>
              {isEditingOrder ? (
                <DateTimeSelectorAdmin
                  selectedDate={selectedDate}
                  onDateChange={setSelectedDate}
                  selectedTime={selectedTime}
                  onTimeChange={setSelectedTime}
                />
              ) : (
                <div className="text-base font-['Open_Sans'] text-black">{orderData.delivery_date}</div>
              )}
            </div>
          )}

          {(orderData.delivery_notes || isEditingOrder) && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Заметки к доставке</div>
              {isEditingOrder ? (
                <textarea
                  value={editedFields.delivery_notes}
                  onChange={(e) => setEditedFields({ ...editedFields, delivery_notes: e.target.value })}
                  placeholder="Дополнительные заметки к доставке"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-border rounded text-base font-['Open_Sans'] text-black focus:outline-none focus:ring-2 focus:ring-purple-primary resize-none"
                  disabled={isUpdatingStatus}
                />
              ) : (
                <div className="text-base font-['Open_Sans'] text-black">{orderData.delivery_notes}</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Payment section */}
      <div className="px-4 pb-6">
        <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px] mb-4">Оплата</h2>

        <div className="space-y-4">
          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Сумма к оплате</div>
            <div className="text-base font-['Open_Sans'] text-black">{orderData.total}</div>
          </div>

          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Статус оплаты</div>
            <div className="text-base font-['Open_Sans'] text-black">
              {orderData.status === 'paid' ? 'Оплачено' : 'Не оплачено'}
            </div>
          </div>

          {/* Kaspi Refund Form - only for DIRECTOR role */}
          {orderData.payment_method === 'kaspi' &&
           orderData.kaspi_payment_status === 'Processed' &&
           (userRole === 'DIRECTOR' || userRole === 'SUPERADMIN') && (
            <div className="pt-4 border-t border-gray-border">
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-2">
                Возврат средств Kaspi Pay
              </div>

              <div className="flex items-center gap-2 mb-2">
                <input
                  type="number"
                  value={refundAmount}
                  onChange={(e) => setRefundAmount(e.target.value)}
                  placeholder={`Максимум ${orderData.totalRaw / 100} ₸`}
                  className="flex-1 px-3 py-2 border border-gray-border rounded text-base font-['Open_Sans'] text-black focus:outline-none focus:ring-2 focus:ring-purple-primary"
                  disabled={isRefunding}
                />
                <span className="text-base font-['Open_Sans'] text-black">₸</span>
              </div>

              <button
                onClick={handleKaspiRefund}
                disabled={isRefunding || !refundAmount || parseFloat(refundAmount) <= 0}
                className="w-full h-[44px] bg-red-500 text-white rounded text-base font-['Open_Sans'] uppercase tracking-[0.8px] hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isRefunding ? 'Возврат...' : 'Вернуть средства'}
              </button>

              <div className="text-xs font-['Open_Sans'] text-gray-disabled mt-2">
                Доступно только для директора. Полный или частичный возврат.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Execution status section */}
      <div className="px-4 pb-6">
        <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px] mb-4">Статус выполнения</h2>

        <div className="space-y-4">
          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Статус</div>
            <div className="relative">
              <button
                onClick={() => setIsStatusDropdownOpen(!isStatusDropdownOpen)}
                disabled={isUpdatingStatus}
                className="w-full flex items-center justify-between cursor-pointer hover:bg-gray-50 rounded px-2 py-1 transition-colors disabled:opacity-50"
              >
                <div className="text-base font-['Open_Sans'] text-black">{orderData.statusLabel}</div>
                <svg
                  className={`w-2.5 h-2.5 text-gray-400 transition-transform ${isStatusDropdownOpen ? 'rotate-180' : ''}`}
                  fill="currentColor"
                  viewBox="0 0 10 10"
                >
                  <path d="M5 7L1 3h8L5 7z"/>
                </svg>
              </button>

              {/* Dropdown menu */}
              {isStatusDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-border rounded shadow-lg z-10 max-h-64 overflow-y-auto">
                  {availableStatuses.map((status) => (
                    <button
                      key={status.id}
                      onClick={() => handleStatusChange(status.id)}
                      disabled={isUpdatingStatus || status.id === orderData.status}
                      className={`w-full px-4 py-2 text-left text-base font-['Open_Sans'] hover:bg-purple-light transition-colors ${
                        status.id === orderData.status ? 'bg-purple-light text-purple-primary font-semibold' : 'text-black'
                      } disabled:opacity-50`}
                    >
                      {status.label}
                      {status.id === orderData.status && (
                        <span className="ml-2 text-xs">✓</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Responsible person assignment */}
          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Ответственный</div>
            <div className="relative">
              <button
                onClick={() => setIsResponsibleDropdownOpen(!isResponsibleDropdownOpen)}
                disabled={isAssigning || loadingTeam}
                className="w-full flex items-center justify-between cursor-pointer hover:bg-gray-50 rounded px-2 py-1 transition-colors disabled:opacity-50"
              >
                <div className="text-base font-['Open_Sans'] text-black">
                  {orderData.assigned_to_name || 'Выбрать'}
                </div>
                <svg
                  className={`w-2.5 h-2.5 text-gray-400 transition-transform ${isResponsibleDropdownOpen ? 'rotate-180' : ''}`}
                  fill="currentColor"
                  viewBox="0 0 10 10"
                >
                  <path d="M5 7L1 3h8L5 7z"/>
                </svg>
              </button>

              {/* Dropdown menu for responsible */}
              {isResponsibleDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-border rounded shadow-lg z-10 max-h-64 overflow-y-auto">
                  {loadingTeam ? (
                    <div className="px-4 py-2 text-sm text-gray-disabled">Загрузка...</div>
                  ) : teamMembers.filter(u => u.role !== 'COURIER').length > 0 ? (
                    teamMembers
                      .filter(u => u.role !== 'COURIER')
                      .map((user) => (
                        <button
                          key={user.id}
                          onClick={() => handleAssignResponsible(user.id)}
                          disabled={isAssigning}
                          className="w-full px-4 py-2 text-left text-base font-['Open_Sans'] hover:bg-purple-light transition-colors disabled:opacity-50"
                        >
                          <div>{user.name}</div>
                          <div className="text-xs text-gray-disabled">{user.role}</div>
                        </button>
                      ))
                  ) : (
                    <div className="px-4 py-2 text-sm text-gray-disabled">Нет доступных сотрудников</div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Courier assignment */}
          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Курьер</div>
            <div className="relative">
              <button
                onClick={() => setIsCourierDropdownOpen(!isCourierDropdownOpen)}
                disabled={isAssigning || loadingTeam}
                className="w-full flex items-center justify-between cursor-pointer hover:bg-gray-50 rounded px-2 py-1 transition-colors disabled:opacity-50"
              >
                <div className="text-base font-['Open_Sans'] text-black">
                  {orderData.courier_name || 'Выбрать'}
                </div>
                <svg
                  className={`w-2.5 h-2.5 text-gray-400 transition-transform ${isCourierDropdownOpen ? 'rotate-180' : ''}`}
                  fill="currentColor"
                  viewBox="0 0 10 10"
                >
                  <path d="M5 7L1 3h8L5 7z"/>
                </svg>
              </button>

              {/* Dropdown menu for courier */}
              {isCourierDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-border rounded shadow-lg z-10 max-h-64 overflow-y-auto">
                  {loadingTeam ? (
                    <div className="px-4 py-2 text-sm text-gray-disabled">Загрузка...</div>
                  ) : teamMembers.filter(u => u.role === 'COURIER').length > 0 ? (
                    teamMembers
                      .filter(u => u.role === 'COURIER')
                      .map((user) => (
                        <button
                          key={user.id}
                          onClick={() => handleAssignCourier(user.id)}
                          disabled={isAssigning}
                          className="w-full px-4 py-2 text-left text-base font-['Open_Sans'] hover:bg-purple-light transition-colors disabled:opacity-50"
                        >
                          {user.name}
                        </button>
                      ))
                  ) : (
                    <div className="px-4 py-2 text-sm text-gray-disabled">Нет доступных курьеров</div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* History section */}
      <div className="px-4 pb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px]">История изменений</h2>
          {orderHistory.length > 0 && (
            <span className="bg-purple-primary text-white text-xs px-2 py-1 rounded-full">
              {orderHistory.length}
            </span>
          )}
        </div>

        {loadingHistory ? (
          <div className="text-sm font-['Open_Sans'] text-gray-disabled">Загрузка истории...</div>
        ) : orderHistory.length > 0 ? (
          <div className="space-y-4">
            {orderHistory.map((entry) => (
              <div key={entry.id} className="border-l-2 border-purple-primary pl-3 py-1">
                <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">
                  {formatTimestamp(entry.changed_at)} ·
                  <span className={entry.changed_by === 'customer' ? 'text-purple-primary font-semibold' : 'text-gray-600'}>
                    {' '}{entry.changed_by === 'customer' ? 'Клиент' : 'Администратор'}
                  </span>
                </div>
                <div className="text-base font-['Open_Sans'] text-black leading-normal">
                  <span className="font-semibold">{formatFieldName(entry.field_name)}</span>
                  <br />
                  <span className="text-gray-disabled line-through">{entry.old_value || '(пусто)'}</span>
                  {' → '}
                  <span className="text-purple-primary font-semibold">{entry.new_value || '(пусто)'}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">{orderData.date} {orderData.time}</div>
              <div className="text-base font-['Open_Sans'] text-black leading-normal">Создание заказа</div>
            </div>
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="px-4 pb-8 space-y-3">
        {/* Next status button - hidden for delivered and cancelled orders */}
        {orderData.status !== 'delivered' && orderData.status !== 'cancelled' && (
          <button
            onClick={handleNextStatus}
            disabled={isUpdatingStatus}
            className="w-full h-[44px] bg-purple-primary rounded text-base font-['Open_Sans'] text-white uppercase tracking-[0.8px] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
          >
            {isUpdatingStatus ? 'Обновление...' : getNextStatusButtonText(orderData.status)}
          </button>
        )}

        {isEditingOrder ? (
          <div className="flex gap-3">
            <button
              onClick={handleSaveOrder}
              disabled={isUpdatingStatus}
              className="flex-1 h-[46px] bg-purple-primary rounded text-base font-['Open_Sans'] text-white uppercase tracking-[1.6px] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
            >
              {isUpdatingStatus ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button
              onClick={handleCancelEditOrder}
              disabled={isUpdatingStatus}
              className="flex-1 h-[46px] bg-white border border-gray-neutral rounded text-base font-['Open_Sans'] text-black uppercase tracking-[1.6px] disabled:opacity-50 hover:bg-gray-50 transition-colors"
            >
              Отмена
            </button>
          </div>
        ) : (
          <button
            onClick={handleEditOrder}
            className="w-full h-[46px] bg-white border border-gray-neutral rounded text-base font-['Open_Sans'] text-black uppercase tracking-[1.6px] hover:bg-gray-50 transition-colors"
          >
            Редактировать
          </button>
        )}

        {/* Cancel button - hidden for already cancelled orders */}
        {orderData.status !== 'cancelled' && (
          <button
            onClick={handleCancelOrder}
            disabled={isUpdatingStatus}
            className="w-full h-[46px] bg-error-primary rounded text-base font-['Open_Sans'] text-white uppercase tracking-[1.6px] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-red-600 transition-colors"
          >
            Отменить заказ
          </button>
        )}
      </div>
    </div>
  );
};

export default OrderDetail;