import React from 'react';
import { useOrder } from './OrderContext';

const OrderItemsList = () => {
  const { orderData } = useOrder();

  if (!orderData || !orderData.items || orderData.items.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg p-4 mb-4">
      <h2 className="text-lg font-semibold mb-4">Товары</h2>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="border-b">
            <tr>
              <th className="text-left py-2 text-sm text-gray-disabled">Товар</th>
              <th className="text-right py-2 text-sm text-gray-disabled">Кол-во</th>
              <th className="text-right py-2 text-sm text-gray-disabled">Цена</th>
              <th className="text-right py-2 text-sm text-gray-disabled">Сумма</th>
            </tr>
          </thead>
          <tbody>
            {orderData.items.map((item, index) => (
              <tr key={index} className="border-b">
                <td className="py-3">
                  <div className="text-sm font-medium">{item.name}</div>
                  {item.description && (
                    <div className="text-xs text-gray-disabled mt-1">{item.description}</div>
                  )}
                  {item.special_requests && (
                    <div className="text-xs text-amber-600 mt-1">
                      Примечание: {item.special_requests}
                    </div>
                  )}
                </td>
                <td className="text-right py-3 text-sm">{item.quantity}</td>
                <td className="text-right py-3 text-sm">{item.price}</td>
                <td className="text-right py-3 text-sm font-medium">{item.total}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-gray-50">
            <tr>
              <td colSpan="3" className="py-3 text-right text-sm font-semibold">
                Подытог:
              </td>
              <td className="text-right py-3 text-sm font-semibold">
                {orderData.subtotal}
              </td>
            </tr>
            {orderData.delivery_cost && orderData.delivery_cost !== '0 ₸' && (
              <tr>
                <td colSpan="3" className="py-2 text-right text-sm">
                  Доставка:
                </td>
                <td className="text-right py-2 text-sm">
                  {orderData.delivery_cost}
                </td>
              </tr>
            )}
            <tr className="border-t-2 border-gray-300">
              <td colSpan="3" className="py-3 text-right text-base font-bold">
                Итого:
              </td>
              <td className="text-right py-3 text-base font-bold text-purple-primary">
                {orderData.total}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default OrderItemsList;
