import React, { createContext, useContext, useState, useEffect } from 'react';
import { ordersAPI, formatOrderForDisplay } from '../../services';

const OrderContext = createContext(null);

export const OrderProvider = ({ orderId, children }) => {
  const [orderData, setOrderData] = useState(null);
  const [recipientInfo, setRecipientInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (orderId) {
      fetchOrder();
    }
  }, [orderId]);

  const fetchOrder = async () => {
    try {
      setLoading(true);
      setError(null);

      const rawOrder = await ordersAPI.getOrder(orderId);
      const formattedOrder = formatOrderForDisplay(rawOrder);

      // Parse recipient info from notes
      // Look for pattern: "Получатель: Name, тел: Phone"
      const recipientMatch = formattedOrder.notes?.match(/Получатель: (.+?), тел: (.+?)(?:\n|$)/);
      if (recipientMatch) {
        setRecipientInfo({
          name: recipientMatch[1],
          phone: recipientMatch[2]
        });
      }

      setOrderData(formattedOrder);
    } catch (err) {
      console.error('Error loading order:', err);
      setError(err.message || 'Failed to load order');
    } finally {
      setLoading(false);
    }
  };

  const refreshOrder = () => {
    return fetchOrder();
  };

  const updateOrderData = (data) => {
    setOrderData(data);
  };

  const toggleEdit = () => {
    setIsEditing(prev => !prev);
  };

  const updateField = (field, value) => {
    setOrderData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const value = {
    orderData,
    recipientInfo,
    loading,
    error,
    isEditing,
    setOrderData: updateOrderData,
    refreshOrder,
    toggleEdit,
    updateField,
    setError
  };

  return (
    <OrderContext.Provider value={value}>
      {children}
    </OrderContext.Provider>
  );
};

export const useOrder = () => {
  const context = useContext(OrderContext);
  if (!context) {
    throw new Error('useOrder must be used within OrderProvider');
  }
  return context;
};
