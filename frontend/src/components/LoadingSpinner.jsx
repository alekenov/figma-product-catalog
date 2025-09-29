import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="figma-container flex items-center justify-center min-h-screen bg-white">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-primary"></div>
        <p className="text-gray-600 text-sm">Загрузка...</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;