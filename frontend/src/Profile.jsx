import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import BottomNavBar from './components/BottomNavBar';
import { ProfileProvider, useProfile } from './components/profile/ProfileContext';
import ProfileInfo from './components/profile/ProfileInfo';
import ShopSettings from './components/profile/ShopSettings';
import './App.css';

const ProfileContent = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { loading, error } = useProfile();
  const [activeNav, setActiveNav] = useState('profile');

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
      // Navigate to login even if logout API call fails
      navigate('/login', { replace: true });
    }
  };

  // Show loading screen
  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex items-center justify-between px-4 mt-5">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
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
            <h1 className="text-2xl font-['Open_Sans'] font-normal">Профиль</h1>
          </div>
        </div>
        <div className="flex items-center justify-center mt-20">
          <div className="text-gray-disabled">Загрузка...</div>
        </div>
        <BottomNavBar
          activeTab={activeNav}
          onTabChange={handleNavChange}
        />
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
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
          <h1 className="text-2xl font-['Open_Sans'] font-normal">Профиль</h1>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="px-3 py-1 text-sm text-gray-disabled border border-gray-neutral rounded-md hover:bg-gray-50 transition-colors"
        >
          Выйти
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-4 mt-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="px-4 mt-6">
        {/* Profile Info & Team Management */}
        <ProfileInfo />

        {/* Shop Settings */}
        <ShopSettings />
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-16" />

      {/* Bottom Navigation */}
      <BottomNavBar
        activeTab={activeNav}
        onTabChange={handleNavChange}
      />
    </div>
  );
};

const Profile = () => {
  return (
    <ProfileProvider>
      <ProfileContent />
    </ProfileProvider>
  );
};

export default Profile;
