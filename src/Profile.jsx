import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import BottomNavBar from './components/BottomNavBar';
import ToggleSwitch from './components/ToggleSwitch';
import { profileAPI, shopAPI } from './services/api';
import './App.css';

const Profile = () => {
  const navigate = useNavigate();
  const { user: userInfo, logout } = useAuth();
  const [activeNav, setActiveNav] = useState('profile');

  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Team members state
  const [teamMembers, setTeamMembers] = useState([]);

  // Shop settings state
  const [shopSettings, setShopSettings] = useState(null);

  // Invite colleague modal state
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [newColleague, setNewColleague] = useState({
    name: '',
    phone: '',
    role: 'MANAGER'
  });

  // Load data on component mount
  useEffect(() => {
    const loadProfileData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load team members and shop settings in parallel
        const [teamData, shopData] = await Promise.all([
          profileAPI.getTeamMembers({ limit: 50 }),
          shopAPI.getShopSettings()
        ]);

        setTeamMembers(teamData);
        setShopSettings(shopData);

      } catch (err) {
        console.error('Error loading profile data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadProfileData();
  }, []);

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

  const handleInviteColleague = async () => {
    if (!newColleague.name || !newColleague.phone) {
      setError('Пожалуйста, заполните все поля');
      return;
    }

    try {
      setInviteLoading(true);
      setError(null);

      await profileAPI.inviteTeamMember({
        name: newColleague.name,
        phone: newColleague.phone,
        role: newColleague.role
      });

      // Reload team members to show the new invitation
      const teamData = await profileAPI.getTeamMembers({ limit: 50 });
      setTeamMembers(teamData);

      setNewColleague({ name: '', phone: '', role: 'MANAGER' });
      setShowInviteModal(false);
    } catch (err) {
      console.error('Error inviting colleague:', err);
      setError(err.message);
    } finally {
      setInviteLoading(false);
    }
  };

  const updateShopSetting = async (section, field, value) => {
    try {
      // Update local state immediately for responsive UI
      const updatedSettings = {
        ...shopSettings,
        [section]: typeof shopSettings[section] === 'object'
          ? { ...shopSettings[section], [field]: value }
          : value
      };
      setShopSettings(updatedSettings);

      // Update via API
      if (section === 'delivery') {
        await shopAPI.updateDeliverySettings({ [field]: value });
      } else {
        await shopAPI.updateShopSettings({ [field || section]: value });
      }
    } catch (err) {
      console.error('Error updating shop setting:', err);
      setError(err.message);
      // Reload shop settings on error to restore correct state
      try {
        const shopData = await shopAPI.getShopSettings();
        setShopSettings(shopData);
      } catch (reloadErr) {
        console.error('Error reloading shop settings:', reloadErr);
      }
    }
  };

  const updateWorkingHours = async (period, field, value) => {
    try {
      // Update local state immediately
      const updatedSettings = {
        ...shopSettings,
        workingHours: {
          ...shopSettings.workingHours,
          [period]: {
            ...shopSettings.workingHours[period],
            [field]: value
          }
        }
      };
      setShopSettings(updatedSettings);

      // Convert frontend format to backend format
      const workingHoursData = {};
      if (period === 'weekdays') {
        workingHoursData[`weekday_${field}`] = value;
      } else if (period === 'weekend') {
        workingHoursData[`weekend_${field}`] = value;
      }

      // Update via API
      await shopAPI.updateWorkingHours(workingHoursData);
    } catch (err) {
      console.error('Error updating working hours:', err);
      setError(err.message);
      // Reload shop settings on error
      try {
        const shopData = await shopAPI.getShopSettings();
        setShopSettings(shopData);
      } catch (reloadErr) {
        console.error('Error reloading shop settings:', reloadErr);
      }
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
            <p className="text-red-700 text-sm">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-500 text-xs underline mt-1"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}

      <div className="px-4 mt-6">
        {/* User Info Section */}
        {userInfo && (
          <div className="bg-gray-input rounded-lg p-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-primary rounded-full flex items-center justify-center">
                <span className="text-white text-lg font-semibold">
                  {userInfo.name?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-['Open_Sans'] font-semibold">{userInfo.name || 'Пользователь'}</h3>
                <p className="text-sm text-gray-disabled">{userInfo.phone}</p>
                <p className="text-sm text-gray-disabled">
                  {userInfo.role === 'DIRECTOR' ? 'Директор' :
                   userInfo.role === 'MANAGER' ? 'Менеджер' :
                   userInfo.role === 'FLORIST' ? 'Флорист' :
                   userInfo.role === 'COURIER' ? 'Курьер' : userInfo.role}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Team Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-['Open_Sans'] font-semibold">Команда</h2>
            {userInfo && (userInfo.role === 'DIRECTOR' || userInfo.role === 'MANAGER') && (
              <button
                onClick={() => setShowInviteModal(true)}
                className="px-3 py-1 bg-purple-primary text-white text-sm rounded-md"
              >
                Пригласить
              </button>
            )}
          </div>

          <div className="space-y-3">
            {teamMembers.map((member) => (
              <div key={member.id} className="bg-gray-input rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="text-sm font-['Open_Sans'] font-semibold">{member.name}</h4>
                    <p className="text-xs text-gray-disabled">{member.phone}</p>
                  </div>
                  <span className="text-xs bg-white px-2 py-1 rounded text-gray-disabled">
                    {member.role === 'DIRECTOR' ? 'Директор' :
                     member.role === 'MANAGER' ? 'Менеджер' :
                     member.role === 'FLORIST' ? 'Флорист' :
                     member.role === 'COURIER' ? 'Курьер' : member.role}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shop Settings */}
        {shopSettings && (
          <div className="mb-6">
            <h2 className="text-lg font-['Open_Sans'] font-semibold mb-4">Настройки магазина</h2>

            {/* Shop Name */}
            <div className="mb-4">
              <label className="block text-sm text-gray-disabled mb-2">Название магазина</label>
              <input
                type="text"
                value={shopSettings.shop_name || ''}
                onChange={(e) => updateShopSetting('shop_name', null, e.target.value)}
                className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                placeholder="Введите название магазина"
              />
            </div>

            {/* Address */}
            <div className="mb-4">
              <label className="block text-sm text-gray-disabled mb-2">Адрес</label>
              <input
                type="text"
                value={shopSettings.address || ''}
                onChange={(e) => updateShopSetting('address', null, e.target.value)}
                className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                placeholder="Введите адрес магазина"
              />
            </div>

            {/* City */}
            <div className="mb-4">
              <label className="block text-sm text-gray-disabled mb-2">Город</label>
              <select
                value={shopSettings.city || 'ALMATY'}
                onChange={(e) => updateShopSetting('city', null, e.target.value)}
                className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
              >
                <option value="ALMATY">Алматы</option>
                <option value="ASTANA">Астана</option>
              </select>
            </div>

            {/* Working Hours */}
            <div className="mb-4">
              <h3 className="text-sm text-gray-disabled mb-3">Время работы</h3>

              {/* Weekdays */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">Будни</span>
                </div>
                <div className="flex gap-3">
                  <input
                    type="time"
                    value={shopSettings.weekday_start || '09:00'}
                    onChange={(e) => updateWorkingHours('weekdays', 'start', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                  <input
                    type="time"
                    value={shopSettings.weekday_end || '18:00'}
                    onChange={(e) => updateWorkingHours('weekdays', 'end', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                </div>
              </div>

              {/* Weekend */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">Выходные</span>
                </div>
                <div className="flex gap-3">
                  <input
                    type="time"
                    value={shopSettings.weekend_start || '10:00'}
                    onChange={(e) => updateWorkingHours('weekend', 'start', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                  <input
                    type="time"
                    value={shopSettings.weekend_end || '17:00'}
                    onChange={(e) => updateWorkingHours('weekend', 'end', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                </div>
              </div>
            </div>
            <div className="mb-6">
              <h2 className="text-lg font-['Open_Sans'] font-semibold mb-4">Доставка</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-disabled mb-2">Стоимость доставки</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={Math.floor((shopSettings.delivery_cost || 0) / 100)}
                      onChange={(e) => updateShopSetting('delivery', 'delivery_cost', (parseInt(e.target.value) || 0) * 100)}
                      className="w-full px-3 py-2 bg-gray-input rounded-md text-sm pr-8"
                      placeholder="0"
                    />
                    <span className="absolute right-3 top-2 text-sm text-gray-disabled">₸</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-disabled mb-2">Сумма для бесплатной доставки</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={Math.floor((shopSettings.free_delivery_amount || 0) / 100)}
                      onChange={(e) => updateShopSetting('delivery', 'free_delivery_amount', (parseInt(e.target.value) || 0) * 100)}
                      className="w-full px-3 py-2 bg-gray-input rounded-md text-sm pr-8"
                      placeholder="0"
                    />
                    <span className="absolute right-3 top-2 text-sm text-gray-disabled">₸</span>
                  </div>
                </div>

                <div className="flex items-center justify-between py-2">
                  <span className="text-sm">Самовывоз доступен</span>
                  <ToggleSwitch
                    isEnabled={shopSettings.pickup_available || false}
                    onToggle={(value) => updateShopSetting('delivery', 'pickup_available', value)}
                  />
                </div>

                <div className="flex items-center justify-between py-2">
                  <span className="text-sm">Доставка доступна</span>
                  <ToggleSwitch
                    isEnabled={shopSettings.delivery_available || false}
                    onToggle={(value) => updateShopSetting('delivery', 'delivery_available', value)}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-16" />

      {/* Invite Colleague Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 mx-4 w-full max-w-sm">
            <h3 className="text-lg font-['Open_Sans'] font-semibold mb-4">Пригласить коллегу</h3>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-disabled mb-2">Имя</label>
                <input
                  type="text"
                  value={newColleague.name}
                  onChange={(e) => setNewColleague({...newColleague, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  placeholder="Введите имя"
                  disabled={inviteLoading}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-disabled mb-2">Телефон</label>
                <input
                  type="tel"
                  value={newColleague.phone}
                  onChange={(e) => setNewColleague({...newColleague, phone: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  placeholder="+7 (___) ___ __ __"
                  disabled={inviteLoading}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-disabled mb-2">Роль</label>
                <select
                  value={newColleague.role}
                  onChange={(e) => setNewColleague({...newColleague, role: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  disabled={inviteLoading}
                >
                  <option value="MANAGER">Менеджер</option>
                  <option value="FLORIST">Флорист</option>
                  <option value="COURIER">Курьер</option>
                  {userInfo && userInfo.role === 'DIRECTOR' && (
                    <option value="DIRECTOR">Директор</option>
                  )}
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowInviteModal(false);
                  setError(null);
                }}
                className="flex-1 px-4 py-2 text-gray-disabled border border-gray-neutral rounded-md text-sm"
                disabled={inviteLoading}
              >
                Отмена
              </button>
              <button
                onClick={handleInviteColleague}
                className="flex-1 px-4 py-2 bg-purple-primary text-white rounded-md text-sm disabled:opacity-50"
                disabled={inviteLoading}
              >
                {inviteLoading ? 'Отправка...' : 'Пригласить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Navigation */}
      <BottomNavBar
        activeTab={activeNav}
        onTabChange={handleNavChange}
      />
    </div>
  );
};

export default Profile;