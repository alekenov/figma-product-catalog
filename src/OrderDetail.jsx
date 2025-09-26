import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import StatusBadge from './components/StatusBadge';
import InfoRow from './components/InfoRow';
import SectionHeader from './components/SectionHeader';
import PhotoUploadSection from './components/PhotoUploadSection';
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
  const { id } = useParams();
  const { showSuccess } = useToast();
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleBack = () => {
    navigate('/orders');
  };

  // Fetch order data from API
  useEffect(() => {
    const fetchOrder = async () => {
      if (!id) {
        setError('Не указан ID заказа');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const rawOrder = await ordersAPI.getOrder(id);
        const formattedOrder = formatOrderForDisplay(rawOrder);
        setOrderData(formattedOrder);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch order:', err);
        setError('Не удалось загрузить данные заказа');
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [id]);

  const handlePhotoUpload = (photoData) => {
    // Update order status to "собран" when photo is uploaded
    showSuccess(`Вы приняли заказ ${orderData?.orderNumber || id}`);
  };

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

        {/* Share button */}
        <button className="absolute right-16 top-[19px] w-6 h-6">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
        </button>
      </div>

      {/* Photo before delivery section */}
      <div className="px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-purple-light rounded-full flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <div className="text-base font-['Open_Sans'] text-black">Фото до доставки</div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mt-1">Не добавлено</div>
          </div>
        </div>
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
                  Количество: {item.quantity} шт.
                  {item.special_requests && (
                    <div className="text-sm text-gray-disabled mt-1">
                      Пожелания: {item.special_requests}
                    </div>
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
          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Получатель</div>
            <div className="text-base font-['Open_Sans'] text-black flex items-center gap-2">
              {orderData.customerName}, <span className="text-purple-primary">{orderData.phone}</span>
              <svg className="w-6 h-6 text-whatsapp" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.108"/>
              </svg>
            </div>
          </div>

          {/* Данные заказчика/отправителя */}
          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Отправитель (Заказчик)</div>
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

          {orderData.delivery_address && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Адрес доставки</div>
              <div className="text-base font-['Open_Sans'] text-black">{orderData.delivery_address}</div>
            </div>
          )}

          {orderData.delivery_date && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Дата доставки</div>
              <div className="text-base font-['Open_Sans'] text-black">{orderData.delivery_date}</div>
            </div>
          )}

          {orderData.delivery_notes && (
            <div>
              <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Заметки к доставке</div>
              <div className="text-base font-['Open_Sans'] text-black">{orderData.delivery_notes}</div>
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
        </div>
      </div>

      {/* Execution status section */}
      <div className="px-4 pb-6">
        <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px] mb-4">Статус выполнения</h2>

        <div className="space-y-4">
          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Статус</div>
            <div className="flex items-center justify-between">
              <div className="text-base font-['Open_Sans'] text-black">{orderData.statusLabel}</div>
              <svg className="w-2.5 h-2.5 text-gray-400" fill="currentColor" viewBox="0 0 10 10">
                <path d="M5 7L1 3h8L5 7z"/>
              </svg>
            </div>
          </div>

          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Ответственный</div>
            <div className="flex items-center justify-between">
              <div className="text-base font-['Open_Sans'] text-black">Выбрать</div>
              <svg className="w-2.5 h-2.5 text-gray-400" fill="currentColor" viewBox="0 0 10 10">
                <path d="M5 7L1 3h8L5 7z"/>
              </svg>
            </div>
          </div>

          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Курьер</div>
            <div className="flex items-center justify-between">
              <div className="text-base font-['Open_Sans'] text-black">Выбрать</div>
              <svg className="w-2.5 h-2.5 text-gray-400" fill="currentColor" viewBox="0 0 10 10">
                <path d="M5 7L1 3h8L5 7z"/>
              </svg>
            </div>
          </div>

          {/* Photo Upload Section for delivery */}
          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Фото до доставки</div>
            <PhotoUploadSection
              orderId={orderData.orderNumber}
              onPhotoUpload={handlePhotoUpload}
            />
          </div>
        </div>
      </div>

      {/* History section */}
      <div className="px-4 pb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px]">История</h2>
          <svg className="w-3 h-3 text-gray-400 rotate-90" fill="currentColor" viewBox="0 0 10 10">
            <path d="M5 7L1 3h8L5 7z"/>
          </svg>
        </div>

        <div className="space-y-6">
          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">{orderData.date} {orderData.time}</div>
            <div className="text-base font-['Open_Sans'] text-black leading-normal">Создание заказа</div>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="px-4 pb-8 space-y-3">
        <button className="w-full h-[44px] bg-purple-primary rounded text-base font-['Open_Sans'] text-white uppercase tracking-[0.8px]">
          Оплачен
        </button>

        <button className="w-full h-[46px] bg-white border border-gray-neutral rounded text-base font-['Open_Sans'] text-black uppercase tracking-[1.6px]">
          Редактировать
        </button>

        <button className="w-full h-[46px] bg-error-primary rounded text-base font-['Open_Sans'] text-white uppercase tracking-[1.6px]">
          Удалить
        </button>
      </div>
    </div>
  );
};

export default OrderDetail;