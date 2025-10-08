import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import './App.css';

/**
 * Login Component
 * Handles user authentication with phone and password
 */
const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, loading } = useAuth();

  const [formData, setFormData] = useState({
    phone: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Get redirect path from state or default to home
  const from = location.state?.from?.pathname || '/';

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, loading, navigate, from]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const formatPhoneNumber = (phone) => {
    // Remove all non-digits
    const digits = phone.replace(/\D/g, '');

    // Add +7 prefix for Kazakhstan numbers if not present
    // Check length first to avoid ambiguity

    // If 10 digits (without country code), add +7
    if (digits.length === 10) {
      return '+7' + digits;
    }

    // If 11 digits starting with 8 (legacy format), replace with +7
    if (digits.length === 11 && digits.startsWith('8')) {
      return '+7' + digits.substring(1);
    }

    // If 11 digits starting with 7 (already has country code), add +
    if (digits.length === 11 && digits.startsWith('7')) {
      return '+' + digits;
    }

    return phone; // Return as-is if format is unclear
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      console.log('🔐 [Login] Starting login process...');
      console.log('📱 [Login] Raw phone input:', formData.phone);
      console.log('🔑 [Login] Password length:', formData.password.length);

      // Validate inputs
      if (!formData.phone || !formData.password) {
        throw new Error('Пожалуйста, заполните все поля');
      }

      // Format phone number
      const formattedPhone = formatPhoneNumber(formData.phone);
      console.log('✅ [Login] Formatted phone:', formattedPhone);

      console.log('🚀 [Login] Calling login API...');
      await login(formattedPhone, formData.password);
      console.log('✅ [Login] Login successful!');

      // Navigation will be handled by useEffect
    } catch (err) {
      console.error('❌ [Login] Login error:', err);
      console.error('   Error details:', err.message, err.stack);
      setError(err.message || 'Произошла ошибка при входе');
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-gray-disabled">Загрузка...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      <div className="flex flex-col min-h-screen">
        {/* Header */}
        <div className="px-4 mt-8">
          <h1 className="text-2xl font-['Open_Sans'] font-bold text-center mb-2">
            Цветы.kz
          </h1>
          <p className="text-gray-disabled text-center text-sm">
            Войдите в систему управления
          </p>
        </div>

        {/* Login Form */}
        <div className="flex-1 flex flex-col justify-center px-4">
          <div className="w-full max-w-sm mx-auto">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Error Display */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}

              {/* Phone Input */}
              <div>
                <label
                  htmlFor="phone"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Телефон
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const currentPhone = formData.phone.trim();
                      if (!currentPhone) {
                        // If empty, add +7
                        setFormData(prev => ({ ...prev, phone: '+7' }));
                      } else if (currentPhone.startsWith('7') && !currentPhone.startsWith('+')) {
                        // If starts with 7 but no +, add +
                        setFormData(prev => ({ ...prev, phone: '+' + currentPhone }));
                      } else if (currentPhone.startsWith('8')) {
                        // If starts with 8, replace with +7
                        setFormData(prev => ({ ...prev, phone: '+7' + currentPhone.substring(1) }));
                      } else if (!currentPhone.startsWith('+')) {
                        // Otherwise add +7 prefix
                        setFormData(prev => ({ ...prev, phone: '+7' + currentPhone }));
                      }
                      // Focus input after adding prefix
                      document.getElementById('phone')?.focus();
                    }}
                    disabled={isLoading}
                    className="px-4 py-3 bg-purple-primary text-white rounded-lg text-sm font-medium hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
                  >
                    +7
                  </button>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="flex-1 px-3 py-3 bg-gray-input rounded-lg text-sm border border-gray-border focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent"
                    placeholder="7015211545 или +77015211545"
                    disabled={isLoading}
                    required
                  />
                </div>
                <p className="mt-1 text-xs text-gray-disabled">
                  Нажмите "+7" чтобы добавить префикс
                </p>
              </div>

              {/* Password Input */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Пароль
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full px-3 py-3 bg-gray-input rounded-lg text-sm border border-gray-border focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent"
                  placeholder="Введите пароль"
                  disabled={isLoading}
                  required
                />
              </div>

              {/* Login Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-purple-primary text-white py-3 px-4 rounded-lg font-medium text-sm hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Вход...' : 'Войти'}
              </button>
            </form>

            {/* Demo Credentials */}
            <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-xs text-gray-disabled text-center mb-2">
                Для демонстрации используйте:
              </p>
              <p className="text-xs text-center">
                <strong>Телефон:</strong> +77015211545
              </p>
              <p className="text-xs text-center">
                <strong>Пароль:</strong> password
              </p>
              <p className="text-xs text-gray-disabled text-center mt-2">
                Можно вводить без "+" (кнопка "+7" добавит автоматически)
              </p>
            </div>

            {/* Register Link */}
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-disabled">
                Нет аккаунта?{' '}
                <Link to="/register" className="text-purple-primary font-medium hover:underline">
                  Зарегистрироваться
                </Link>
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-6 text-center">
          <p className="text-xs text-gray-disabled">
            © 2024 Цветы.kz. Система управления цветочным магазином
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;