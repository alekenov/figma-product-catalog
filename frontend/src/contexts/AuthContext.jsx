import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, getStoredUser, removeToken } from '../services/api';

/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */
const AuthContext = createContext(null);

/**
 * Hook to use authentication context
 * @returns {Object} Authentication context value
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Authentication Provider Component
 * Manages authentication state and provides auth methods to children
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  /**
   * Check if user is authenticated and load user data
   */
  const checkAuthStatus = async () => {
    console.log('🔍 [AuthContext] Checking auth status...');

    try {
      // Check if user is authenticated based on stored data
      const hasToken = authAPI.isAuthenticated();
      console.log('   Has token:', hasToken);

      if (hasToken) {
        const storedUser = getStoredUser();
        console.log('   Stored user:', storedUser ? storedUser.name : 'none');

        if (storedUser) {
          setUser(storedUser);
          setIsAuthenticated(true);
          console.log('✅ [AuthContext] Using stored user, verifying token...');

          // Verify token is still valid by fetching fresh user data
          try {
            const freshUser = await authAPI.me();
            setUser(freshUser);
            console.log('✅ [AuthContext] Token verified, user refreshed');
          } catch (error) {
            // Token might be expired, try to refresh or logout
            console.warn('⚠️  [AuthContext] Token verification failed:', error.message);
            if (error.message.includes('Сессия истекла') || error.message.includes('401')) {
              console.log('🚪 [AuthContext] Token expired, logging out');
              handleLogout();
              return;
            }
          }
        } else {
          // No stored user but token exists, fetch user data
          console.log('📥 [AuthContext] Fetching user data...');
          try {
            const userData = await authAPI.me();
            setUser(userData);
            setIsAuthenticated(true);
            console.log('✅ [AuthContext] User data fetched:', userData.name);
          } catch (error) {
            console.error('❌ [AuthContext] Failed to fetch user data:', error);
            handleLogout();
          }
        }
      } else {
        console.log('ℹ️  [AuthContext] No token found, user not authenticated');
      }
    } catch (error) {
      console.error('❌ [AuthContext] Auth status check failed:', error);
      handleLogout();
    } finally {
      setLoading(false);
      console.log('✅ [AuthContext] Auth check completed, loading=false');
    }
  };

  /**
   * Login user with phone and password
   * @param {string} phone User phone number
   * @param {string} password User password
   * @returns {Promise<Object>} Login response
   */
  const login = async (phone, password) => {
    try {
      console.log('🔑 [AuthContext] Login method called');
      console.log('   Phone:', phone);

      const loginResponse = await authAPI.login(phone, password);

      console.log('✅ [AuthContext] Login response received:', {
        hasToken: !!loginResponse.access_token,
        userId: loginResponse.user?.id,
        userName: loginResponse.user?.name,
        userRole: loginResponse.user?.role,
        shopId: loginResponse.user?.shop_id
      });

      setUser(loginResponse.user);
      setIsAuthenticated(true);
      console.log('✅ [AuthContext] User state updated, isAuthenticated=true');

      return loginResponse;
    } catch (error) {
      console.error('❌ [AuthContext] Login failed:', error);
      console.error('   Error type:', error.constructor.name);
      console.error('   Error message:', error.message);
      throw error;
    }
  };

  /**
   * Register new user
   * @param {Object} userData User registration data
   * @returns {Promise<Object>} Registration response
   */
  const register = async (userData) => {
    try {
      const user = await authAPI.register(userData);
      // Note: Registration doesn't automatically log in the user
      // They need to login separately after registration
      return user;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  /**
   * Logout current user
   */
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local logout even if API call fails
    } finally {
      handleLogout();
    }
  };

  /**
   * Handle logout cleanup
   */
  const handleLogout = () => {
    removeToken();
    setUser(null);
    setIsAuthenticated(false);
  };

  /**
   * Change user password
   * @param {string} currentPassword Current password
   * @param {string} newPassword New password
   * @returns {Promise<Object>} Success response
   */
  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await authAPI.changePassword(currentPassword, newPassword);
      return response;
    } catch (error) {
      console.error('Password change failed:', error);
      throw error;
    }
  };

  /**
   * Update user profile and refresh context
   * @param {Object} userData Updated user data
   * @returns {Promise<Object>} Updated user
   */
  const updateUser = async (userData) => {
    try {
      // This would typically use profileAPI.updateProfile
      // but we'll keep it simple for now
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      return updatedUser;
    } catch (error) {
      console.error('User update failed:', error);
      throw error;
    }
  };

  /**
   * Check if current user has required role
   * @param {string|string[]} requiredRoles Required role(s)
   * @returns {boolean} True if user has required role
   */
  const hasRole = (requiredRoles) => {
    if (!user || !user.role) return false;

    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
    return roles.includes(user.role);
  };

  /**
   * Check if current user is director
   * @returns {boolean} True if user is director
   */
  const isDirector = () => hasRole('DIRECTOR');

  /**
   * Check if current user is manager or director
   * @returns {boolean} True if user is manager or director
   */
  const isManagerOrDirector = () => hasRole(['MANAGER', 'DIRECTOR']);

  /**
   * Check if current user is superadmin
   * @returns {boolean} True if user is superadmin
   */
  const isSuperadmin = () => user?.is_superadmin === true;

  const value = {
    // State
    user,
    loading,
    isAuthenticated,

    // Methods
    login,
    register,
    logout,
    changePassword,
    updateUser,
    checkAuthStatus,

    // Role checks
    hasRole,
    isDirector,
    isManagerOrDirector,
    isSuperadmin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;