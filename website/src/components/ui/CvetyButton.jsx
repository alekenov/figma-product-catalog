import React from 'react';

/**
 * CvetyButton - универсальный компонент кнопки для дизайн-системы
 *
 * @param {string} variant - Вариант кнопки: 'primary' | 'secondary' | 'ghost' | 'link'
 * @param {string} size - Размер: 'sm' | 'md' | 'lg'
 * @param {boolean} fullWidth - Растянуть на всю ширину
 * @param {boolean} disabled - Заблокирована ли кнопка
 * @param {ReactNode} leftIcon - Иконка слева
 * @param {ReactNode} rightIcon - Иконка справа
 * @param {function} onClick - Обработчик клика
 * @param {string} className - Дополнительные классы
 * @param {ReactNode} children - Содержимое кнопки
 */
export default function CvetyButton({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  leftIcon,
  rightIcon,
  onClick,
  className = '',
  children,
  ...props
}) {
  // Базовые классы
  const baseClasses = 'font-sans font-normal transition-colors inline-flex items-center justify-center gap-2';

  // Варианты стилей
  const variantClasses = {
    primary: 'bg-pink text-white hover:bg-pink/90 disabled:bg-bg-light disabled:text-text-grey-dark',
    secondary: 'bg-white border-2 border-pink text-pink hover:bg-pink/5 disabled:border-bg-light disabled:text-text-grey-dark',
    ghost: 'bg-bg-light text-text-black hover:bg-bg-extra-light disabled:text-text-grey-dark',
    link: 'bg-transparent text-pink hover:underline disabled:text-text-grey-dark p-0'
  };

  // Размеры
  const sizeClasses = {
    sm: 'px-3 py-1 text-body-2 rounded-full',
    md: 'px-6 py-3.5 text-body-1 rounded-full',
    lg: 'px-6 py-4 text-body-1 rounded-lg'
  };

  // Ширина
  const widthClass = fullWidth ? 'w-full' : '';

  // Собираем все классы
  const buttonClasses = [
    baseClasses,
    variantClasses[variant] || variantClasses.primary,
    sizeClasses[size] || sizeClasses.md,
    widthClass,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={buttonClasses}
      {...props}
    >
      {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
      {children}
      {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
    </button>
  );
}