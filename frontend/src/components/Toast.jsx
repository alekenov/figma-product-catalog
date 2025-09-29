import React, { useState, useEffect } from 'react';

const Toast = ({
  message,
  type = 'success',
  duration = 3000,
  onClose,
  isVisible = false
}) => {
  const [show, setShow] = useState(isVisible);

  useEffect(() => {
    setShow(isVisible);
  }, [isVisible]);

  useEffect(() => {
    if (show && duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [show, duration]);

  const handleClose = () => {
    setShow(false);
    if (onClose) {
      setTimeout(onClose, 150); // Wait for fade animation
    }
  };

  const getToastStyles = () => {
    const baseStyles = 'fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-4 py-3 rounded-lg shadow-lg transition-all duration-150 ease-in-out';
    const typeStyles = {
      success: 'bg-success text-white',
      error: 'bg-error-primary text-white',
      info: 'bg-purple-primary text-white'
    };

    const visibilityStyles = show
      ? 'opacity-100 translate-y-0'
      : 'opacity-0 -translate-y-2 pointer-events-none';

    return `${baseStyles} ${typeStyles[type]} ${visibilityStyles}`;
  };

  return (
    <div className={getToastStyles()}>
      <div className="flex items-center gap-3">
        <span className="text-sm font-['Open_Sans'] font-medium">
          {message}
        </span>
        <button
          onClick={handleClose}
          className="text-white hover:text-gray-200 transition-colors"
          aria-label="Закрыть уведомление"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M12 4L4 12M4 4L12 12"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Toast;