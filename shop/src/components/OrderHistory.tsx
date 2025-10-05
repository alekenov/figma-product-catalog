import { useState } from 'react';

interface OrderItem {
  id: string;
  name: string;
  quantity: number;
  price: number;
  image: string;
}

interface Order {
  id: string;
  number: string;
  date: string;
  status: "pending" | "processing" | "shipped" | "delivered" | "cancelled";
  total: number;
  items: OrderItem[];
  recipient: string;
  address: string;
  deliveryDate: string;
  rating?: number;
}

const mockOrders: Order[] = [
  {
    id: "1",
    number: "CVT-2024-001",
    date: "2024-03-15",
    status: "delivered",
    total: 12500,
    recipient: "Мария Петрова",
    address: "г. Астана, ул. Сарайшык, 127",
    deliveryDate: "2024-03-16",
    rating: 5,
    items: []
  },
  {
    id: "2",
    number: "CVT-2024-002",
    date: "2024-03-20",
    status: "shipped",
    total: 15000,
    recipient: "Анна Смирнова",
    address: "г. Астана, пр. Туран, 37",
    deliveryDate: "2024-03-21",
    items: []
  },
  {
    id: "3",
    number: "CVT-2024-003",
    date: "2024-03-10",
    status: "processing",
    total: 8500,
    recipient: "Елена Козлова",
    address: "г. Астана, ул. Кенесары, 56",
    deliveryDate: "2024-03-25",
    items: []
  }
];

export function OrderHistory() {
  const [orders] = useState<Order[]>(mockOrders);

  const getStatusText = (status: Order["status"]) => {
    const statusMap = {
      pending: "Ожидает подтверждения",
      processing: "Готовится к отправке",
      shipped: "В пути",
      delivered: "Доставлен",
      cancelled: "Отменен",
    };
    return statusMap[status];
  };

  const getStatusColor = (status: Order["status"]) => {
    const colorMap = {
      pending: "var(--text-secondary)",
      processing: "var(--brand-primary)",
      shipped: "var(--brand-primary)",
      delivered: "var(--brand-success)",
      cancelled: "var(--text-secondary)",
    };
    return colorMap[status];
  };

  const StatusBadge = ({ status }: { status: Order["status"] }) => (
    <span
      className="px-2 py-1 rounded-full text-micro"
      style={{
        backgroundColor: `${getStatusColor(status)}10`,
        color: getStatusColor(status),
      }}
    >
      {getStatusText(status)}
    </span>
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("ru-RU", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  return (
    <div className="p-[var(--spacing-4)] bg-white space-y-[var(--spacing-4)]">
      <h2 className="text-title text-[var(--text-primary)]">
        История заказов
      </h2>

      <div className="space-y-[var(--spacing-2)]">
        {orders.map((order) => (
          <div
            key={order.id}
            className="p-[var(--spacing-3)] bg-[var(--background-secondary)]"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-body-emphasis text-[var(--text-primary)]">
                  {order.number}
                </p>
                <p className="text-caption text-[var(--text-secondary)]">
                  {formatDate(order.date)}
                </p>
              </div>
              <div className="text-right">
                <StatusBadge status={order.status} />
                <p className="text-price text-[var(--text-primary)]">
                  {order.total.toLocaleString()} ₸
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {orders.length === 0 && (
        <div className="text-center py-8">
          <p className="text-[var(--text-secondary)]">
            Заказов не найдено
          </p>
        </div>
      )}
    </div>
  );
}