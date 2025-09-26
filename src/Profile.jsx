import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import ToggleSwitch from './components/ToggleSwitch';
import './App.css';

const Profile = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('profile');

  // User info state
  const [userInfo, setUserInfo] = useState({
    name: 'Алексей Кенов',
    phone: '+7 701 521 15 45',
    role: 'Директор'
  });

  // Team members state
  const [teamMembers, setTeamMembers] = useState([
    { id: 1, name: 'Анна Смирнова', phone: '+7 701 234 56 78', role: 'Менеджер' },
    { id: 2, name: 'Максим Петров', phone: '+7 701 345 67 89', role: 'Флорист' }
  ]);

  // Shop settings state
  const [shopSettings, setShopSettings] = useState({
    address: 'ул. Абая 15, кв. 25',
    city: 'Алматы',
    workingHours: {
      weekdays: { start: '09:00', end: '18:00', isWeekend: false },
      weekend: { start: '10:00', end: '16:00', isWeekend: false }
    },
    delivery: {
      cost: 1500,
      freeDeliveryAmount: 15000,
      pickupAvailable: true,
      deliveryAvailable: true
    }
  });

  // Invite colleague modal state
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [newColleague, setNewColleague] = useState({
    name: '',
    phone: '',
    role: 'Менеджер'
  });

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  const handleInviteColleague = () => {
    if (newColleague.name && newColleague.phone) {
      setTeamMembers([...teamMembers, {
        id: Date.now(),
        ...newColleague
      }]);
      setNewColleague({ name: '', phone: '', role: 'Менеджер' });
      setShowInviteModal(false);
    }
  };

  const updateShopSetting = (section, field, value) => {
    setShopSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const updateWorkingHours = (period, field, value) => {
    setShopSettings(prev => ({
      ...prev,
      workingHours: {
        ...prev.workingHours,
        [period]: {
          ...prev.workingHours[period],
          [field]: value
        }
      }
    }));
  };

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
      </div>

      <div className="px-4 mt-6">
        {/* User Info Section */}
        <div className="bg-gray-input rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-primary rounded-full flex items-center justify-center">
              <span className="text-white text-lg font-semibold">
                {userInfo.name.charAt(0)}
              </span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-['Open_Sans'] font-semibold">{userInfo.name}</h3>
              <p className="text-sm text-gray-disabled">{userInfo.phone}</p>
              <p className="text-sm text-gray-disabled">{userInfo.role}</p>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-['Open_Sans'] font-semibold">Команда</h2>
            <button
              onClick={() => setShowInviteModal(true)}
              className="px-3 py-1 bg-purple-primary text-white text-sm rounded-md"
            >
              Пригласить
            </button>
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
                    {member.role}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shop Settings */}
        <div className="mb-6">
          <h2 className="text-lg font-['Open_Sans'] font-semibold mb-4">Настройки магазина</h2>

          {/* Address */}
          <div className="mb-4">
            <label className="block text-sm text-gray-disabled mb-2">Адрес</label>
            <input
              type="text"
              value={shopSettings.address}
              onChange={(e) => updateShopSetting('address', null, e.target.value)}
              className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
              placeholder="Введите адрес магазина"
            />
          </div>

          {/* City */}
          <div className="mb-4">
            <label className="block text-sm text-gray-disabled mb-2">Город</label>
            <select
              value={shopSettings.city}
              onChange={(e) => updateShopSetting('city', null, e.target.value)}
              className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
            >
              <option value="Алматы">Алматы</option>
              <option value="Астана">Астана</option>
            </select>
          </div>

          {/* Working Hours */}
          <div className="mb-4">
            <h3 className="text-sm text-gray-disabled mb-3">Время работы</h3>

            {/* Weekdays */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm">Будни</span>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={shopSettings.workingHours.weekdays.isWeekend}
                    onChange={(e) => updateWorkingHours('weekdays', 'isWeekend', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-xs text-gray-disabled">Выходной</span>
                </label>
              </div>
              {!shopSettings.workingHours.weekdays.isWeekend && (
                <div className="flex gap-3">
                  <input
                    type="time"
                    value={shopSettings.workingHours.weekdays.start}
                    onChange={(e) => updateWorkingHours('weekdays', 'start', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                  <input
                    type="time"
                    value={shopSettings.workingHours.weekdays.end}
                    onChange={(e) => updateWorkingHours('weekdays', 'end', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                </div>
              )}
            </div>

            {/* Weekend */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm">Выходные</span>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={shopSettings.workingHours.weekend.isWeekend}
                    onChange={(e) => updateWorkingHours('weekend', 'isWeekend', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-xs text-gray-disabled">Выходной</span>
                </label>
              </div>
              {!shopSettings.workingHours.weekend.isWeekend && (
                <div className="flex gap-3">
                  <input
                    type="time"
                    value={shopSettings.workingHours.weekend.start}
                    onChange={(e) => updateWorkingHours('weekend', 'start', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                  <input
                    type="time"
                    value={shopSettings.workingHours.weekend.end}
                    onChange={(e) => updateWorkingHours('weekend', 'end', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm"
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Delivery Settings */}
        <div className="mb-6">
          <h2 className="text-lg font-['Open_Sans'] font-semibold mb-4">Доставка</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-disabled mb-2">Стоимость доставки</label>
              <div className="relative">
                <input
                  type="number"
                  value={shopSettings.delivery.cost}
                  onChange={(e) => updateShopSetting('delivery', 'cost', parseInt(e.target.value) || 0)}
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
                  value={shopSettings.delivery.freeDeliveryAmount}
                  onChange={(e) => updateShopSetting('delivery', 'freeDeliveryAmount', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm pr-8"
                  placeholder="0"
                />
                <span className="absolute right-3 top-2 text-sm text-gray-disabled">₸</span>
              </div>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Самовывоз доступен</span>
              <ToggleSwitch
                isEnabled={shopSettings.delivery.pickupAvailable}
                onToggle={(value) => updateShopSetting('delivery', 'pickupAvailable', value)}
              />
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Доставка доступна</span>
              <ToggleSwitch
                isEnabled={shopSettings.delivery.deliveryAvailable}
                onToggle={(value) => updateShopSetting('delivery', 'deliveryAvailable', value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-16" />

      {/* Invite Colleague Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 mx-4 w-full max-w-sm">
            <h3 className="text-lg font-['Open_Sans'] font-semibold mb-4">Пригласить коллегу</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-disabled mb-2">Имя</label>
                <input
                  type="text"
                  value={newColleague.name}
                  onChange={(e) => setNewColleague({...newColleague, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  placeholder="Введите имя"
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
                />
              </div>

              <div>
                <label className="block text-sm text-gray-disabled mb-2">Роль</label>
                <select
                  value={newColleague.role}
                  onChange={(e) => setNewColleague({...newColleague, role: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                >
                  <option value="Менеджер">Менеджер</option>
                  <option value="Флорист">Флорист</option>
                  <option value="Курьер">Курьер</option>
                  <option value="Директор">Директор</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="flex-1 px-4 py-2 text-gray-disabled border border-gray-neutral rounded-md text-sm"
              >
                Отмена
              </button>
              <button
                onClick={handleInviteColleague}
                className="flex-1 px-4 py-2 bg-purple-primary text-white rounded-md text-sm"
              >
                Пригласить
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