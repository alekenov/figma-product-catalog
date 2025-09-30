import React from 'react';
import { CvetyStatus } from './ui/cvety-status';

/**
 * OrderProgressBar - адаптер над CvetyStatus для прогресса заказа
 *
 * @param {string} currentStage - Текущая стадия ('confirmed' | 'preparing' | 'delivering')
 */
export default function OrderProgressBar({ currentStage = 'confirmed' }) {
  const steps = [
    { label: 'подтвержден', completed: true },
    { label: 'собираем', completed: currentStage === 'preparing' || currentStage === 'delivering' },
    { label: 'доставляем', completed: currentStage === 'delivering' }
  ];

  return <CvetyStatus steps={steps} />;
}
