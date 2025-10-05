import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Protected Route Component
 * Redirects unauthenticated users to login page
 * Optionally checks for required roles
 */
const ProtectedRoute = ({
  children,
  requiredRoles = null,
  redirectTo = '/login',
  fallback = null
}) => {
  const { isAuthenticated, loading, user, hasRole } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-gray-disabled">Проверка авторизации...</div>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check role requirements if specified
  if (requiredRoles && !hasRole(requiredRoles)) {
    // Show fallback component or error message for insufficient permissions
    if (fallback) {
      return fallback;
    }

    return (
      <div className="figma-container bg-white">
        <div className="flex flex-col items-center justify-center min-h-screen px-4">
          <div className="text-center">
            <h2 className="text-xl font-['Open_Sans'] font-semibold mb-2">
              Недостаточно прав
            </h2>
            <p className="text-gray-disabled mb-4">
              У вас нет прав доступа к этой странице.
            </p>
            <button
              onClick={() => window.history.back()}
              className="px-4 py-2 bg-purple-primary text-white rounded-md text-sm"
            >
              Назад
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render protected content
  return children;
};

/**
 * Manager/Director Only Route
 * Convenience wrapper for routes that require manager or director role
 */
export const ManagerRoute = ({ children, ...props }) => {
  return (
    <ProtectedRoute
      requiredRoles={['MANAGER', 'DIRECTOR']}
      {...props}
    >
      {children}
    </ProtectedRoute>
  );
};

/**
 * Director Only Route
 * Convenience wrapper for routes that require director role
 */
export const DirectorRoute = ({ children, ...props }) => {
  return (
    <ProtectedRoute
      requiredRoles="DIRECTOR"
      {...props}
    >
      {children}
    </ProtectedRoute>
  );
};

/**
 * Superadmin Only Route
 * Convenience wrapper for routes that require superadmin access
 */
export const SuperadminRoute = ({ children, ...props }) => {
  const { isSuperadmin } = useAuth();

  if (!isSuperadmin()) {
    return (
      <div className="figma-container bg-white">
        <div className="flex flex-col items-center justify-center min-h-screen px-4">
          <div className="text-center">
            <h2 className="text-xl font-['Open_Sans'] font-semibold mb-2">
              Доступ запрещен
            </h2>
            <p className="text-gray-disabled mb-4">
              Эта страница доступна только супер-админам.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 bg-purple-primary text-white rounded-md text-sm"
            >
              На главную
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <ProtectedRoute {...props}>{children}</ProtectedRoute>;
};

export default ProtectedRoute;