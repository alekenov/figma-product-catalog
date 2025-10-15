/**
 * Order Form Context
 * Manages order form state (recipient data, customer data, address, delivery time)
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface RecipientData {
  name: string;
  phone: string;
}

export interface CustomerData {
  phone: string;
}

export interface DeliveryAddressData {
  address: string;
  floor: string;
  apartment: string;
  additionalInfo: string;
  askRecipient: boolean;
}

export interface PickupLocationData {
  locationId: string | null;
  address: string;
}

export interface DeliveryTimeData {
  selectedDate: string;  // 'today' | 'tomorrow'
  selectedTimeSlot: string;  // 'express' | 'slot1' | etc.
  selectedTimeLabel: string;  // '120-150 мин' | '18:00-19:00' | etc.
}

interface OrderFormContextValue {
  // Recipient data (for delivery only)
  recipient: RecipientData;
  setRecipient: (data: RecipientData) => void;

  // Customer data (always required)
  customer: CustomerData;
  setCustomer: (data: CustomerData) => void;

  // Delivery address (for delivery only)
  deliveryAddress: DeliveryAddressData;
  setDeliveryAddress: (data: DeliveryAddressData) => void;

  // Pickup location (for pickup only)
  pickupLocation: PickupLocationData;
  setPickupLocation: (data: PickupLocationData) => void;

  // Delivery time
  deliveryTime: DeliveryTimeData;
  setDeliveryTime: (data: DeliveryTimeData) => void;

  // Reset all form data
  reset: () => void;
}

const OrderFormContext = createContext<OrderFormContextValue | null>(null);

// ============================================================================
// Provider
// ============================================================================

interface OrderFormProviderProps {
  children: ReactNode;
}

const initialRecipient: RecipientData = {
  name: '',
  phone: ''
};

const initialCustomer: CustomerData = {
  phone: ''
};

const initialDeliveryAddress: DeliveryAddressData = {
  address: '',
  floor: '',
  apartment: '',
  additionalInfo: '',
  askRecipient: false
};

const initialPickupLocation: PickupLocationData = {
  locationId: null,
  address: ''
};

const initialDeliveryTime: DeliveryTimeData = {
  selectedDate: 'today',
  selectedTimeSlot: 'express',
  selectedTimeLabel: '120-150 мин'
};

export function OrderFormProvider({ children }: OrderFormProviderProps) {
  const [recipient, setRecipient] = useState<RecipientData>(initialRecipient);
  const [customer, setCustomer] = useState<CustomerData>(initialCustomer);
  const [deliveryAddress, setDeliveryAddress] = useState<DeliveryAddressData>(initialDeliveryAddress);
  const [pickupLocation, setPickupLocation] = useState<PickupLocationData>(initialPickupLocation);
  const [deliveryTime, setDeliveryTime] = useState<DeliveryTimeData>(initialDeliveryTime);

  const reset = () => {
    setRecipient(initialRecipient);
    setCustomer(initialCustomer);
    setDeliveryAddress(initialDeliveryAddress);
    setPickupLocation(initialPickupLocation);
    setDeliveryTime(initialDeliveryTime);
  };

  const value: OrderFormContextValue = {
    recipient,
    setRecipient,
    customer,
    setCustomer,
    deliveryAddress,
    setDeliveryAddress,
    pickupLocation,
    setPickupLocation,
    deliveryTime,
    setDeliveryTime,
    reset
  };

  return <OrderFormContext.Provider value={value}>{children}</OrderFormContext.Provider>;
}

/**
 * Hook to access order form context
 */
export function useOrderForm(): OrderFormContextValue {
  const context = useContext(OrderFormContext);

  if (!context) {
    throw new Error('useOrderForm must be used within OrderFormProvider');
  }

  return context;
}
