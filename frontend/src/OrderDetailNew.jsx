import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { OrderProvider, useOrder } from './components/orders/OrderContext';
import OrderInfo from './components/orders/OrderInfo';
import OrderStatusManager from './components/orders/OrderStatusManager';
import OrderItemsList from './components/orders/OrderItemsList';
import OrderPhotos from './components/orders/OrderPhotos';
import './App.css';

const OrderDetailContent = () => {
  const navigate = useNavigate();
  const { orderData, loading, error } = useOrder();

  const handleBack = () => {
    navigate('/orders');
  };

  // Show loading screen
  if (loading) {
    return (
      <div className="figma-container bg-white min-h-screen">
        <div className="flex items-center justify-between px-4 mt-5">
          <div className="flex items-center gap-3">
            <button
              onClick={handleBack}
              className="w-6 h-6 flex items-center justify-center"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 18l-6-6 6-6"
                />
              </svg>
            </button>
            <h1 className="text-2xl font-['Open_Sans'] font-normal">Заказ</h1>
          </div>
        </div>
        <div className="flex items-center justify-center mt-20">
          <div className="text-gray-disabled">Загрузка...</div>
        </div>
      </div>
    );
  }

  // Show error screen
  if (error) {
    return (
      <div className="figma-container bg-white min-h-screen">
        <div className="flex items-center justify-between px-4 mt-5">
          <div className="flex items-center gap-3">
            <button
              onClick={handleBack}
              className="w-6 h-6 flex items-center justify-center"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 18l-6-6 6-6"
                />
              </svg>
            </button>
            <h1 className="text-2xl font-['Open_Sans'] font-normal">Заказ</h1>
          </div>
        </div>
        <div className="px-4 mt-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!orderData) return null;

  return (
    <div className="figma-container bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="flex items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <button
              onClick={handleBack}
              className="w-6 h-6 flex items-center justify-center"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 18l-6-6 6-6"
                />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-['Open_Sans'] font-semibold">
                {orderData.orderNumber}
              </h1>
              <p className="text-xs text-gray-disabled">
                {orderData.customerName}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-4 space-y-4">
        <OrderStatusManager />
        <OrderInfo />
        <OrderItemsList />
        <OrderPhotos />
      </div>

      {/* Bottom spacing */}
      <div className="h-16" />
    </div>
  );
};

const OrderDetailNew = () => {
  const { orderId } = useParams();

  return (
    <OrderProvider orderId={orderId}>
      <OrderDetailContent />
    </OrderProvider>
  );
};

export default OrderDetailNew;
