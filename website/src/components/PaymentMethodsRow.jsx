import React from 'react';
import { VisaIcon, MastercardIcon, MirIcon, PayPalIcon } from '../assets/icons/SocialIcons';

/**
 * Payment Methods Row Component
 * Displays payment method icons in a horizontal row
 * Adapted for Kazakhstan market (includes Visa, Mastercard, Mir)
 */
export default function PaymentMethodsRow() {
  return (
    <div className="flex gap-2 items-center">
      <VisaIcon className="h-8" />
      <MastercardIcon className="h-8" />
      <MirIcon className="h-8" />
      <PayPalIcon className="h-8" />
    </div>
  );
}