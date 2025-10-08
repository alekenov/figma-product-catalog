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
  const [teamInvitations, setTeamInvitations] = useState([]);

  // Shop settings state
  const [shopSettings, setShopSettings] = useState(null);

  // Edit mode states for shop settings
  const [isEditing, setIsEditing] = useState(false);
  const [editedSettings, setEditedSettings] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  const [errorType, setErrorType] = useState(null); // 'network' | 'validation' | null

  // Invite colleague modal state
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showInviteSuccessModal, setShowInviteSuccessModal] = useState(false);
  const [invitationCode, setInvitationCode] = useState('');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [newColleague, setNewColleague] = useState({
    name: '',
    phone: '',
    role: 'MANAGER'
  });

  // Edit member state
  const [editingMemberId, setEditingMemberId] = useState(null);
  const [editedRole, setEditedRole] = useState('');
  const [updateLoading, setUpdateLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Load data on component mount
  useEffect(() => {
    const loadProfileData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load team members, invitations and shop settings in parallel
        const [teamData, invitationsData, shopData] = await Promise.all([
          profileAPI.getTeamMembers({ limit: 50 }),
          profileAPI.getTeamInvitations(),
          shopAPI.getShopSettings()
        ]);

        setTeamMembers(teamData);
        setTeamInvitations(invitationsData || []);
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

      const invitation = await profileAPI.inviteTeamMember({
        name: newColleague.name,
        phone: newColleague.phone,
        role: newColleague.role.toLowerCase()
      });

      // Reload team members and invitations
      const [teamData, invitationsData] = await Promise.all([
        profileAPI.getTeamMembers({ limit: 50 }),
        profileAPI.getTeamInvitations()
      ]);
      setTeamMembers(teamData);
      setTeamInvitations(invitationsData || []);

      // Show success modal with invitation code
      setInvitationCode(invitation.invitation_code);
      setNewColleague({ name: '', phone: '', role: 'MANAGER' });
      setShowInviteModal(false);
      setShowInviteSuccessModal(true);
    } catch (err) {
      console.error('Error inviting colleague:', err);
      setError(err.message);
    } finally {
      setInviteLoading(false);
    }
  };

  const handleEditMember = (member) => {
    setEditingMemberId(member.id);
    // Normalize role to lowercase for consistency
    setEditedRole(member.role.toLowerCase());
  };

  const handleCancelEdit = () => {
    setEditingMemberId(null);
    setEditedRole('');
  };

  const handleUpdateRole = async (userId) => {
    try {
      setUpdateLoading(true);
      setError(null);

      await profileAPI.changeTeamMemberRole(userId, editedRole.toLowerCase());

      // Reload team members
      const teamData = await profileAPI.getTeamMembers({ limit: 50 });
      setTeamMembers(teamData);

      setEditingMemberId(null);
      setEditedRole('');
    } catch (err) {
      console.error('Error updating role:', err);
      setError(err.message);
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleDeleteMember = async (userId, memberName) => {
    if (!confirm(`Удалить ${memberName} из команды?`)) {
      return;
    }

    try {
      setDeleteLoading(true);
      setError(null);

      await profileAPI.removeTeamMember(userId);

      // Reload team members
      const teamData = await profileAPI.getTeamMembers({ limit: 50 });
      setTeamMembers(teamData);

      setEditingMemberId(null);
    } catch (err) {
      console.error('Error deleting member:', err);
      setError(err.message);
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleCancelInvitation = async (invitationId) => {
    if (!confirm('Отменить это приглашение?')) {
      return;
    }

    try {
      setError(null);
      await profileAPI.cancelInvitation(invitationId);

      // Reload invitations
      const invitationsData = await profileAPI.getTeamInvitations();
      setTeamInvitations(invitationsData || []);
    } catch (err) {
      console.error('Error canceling invitation:', err);
      setError(err.message);
    }
  };

  const canEditMember = (member) => {
    if (!userInfo) return false;
    if (member.id === userInfo.id) return false; // Can't edit yourself

    const isDirector = userInfo.role === 'director' || userInfo.role === 'DIRECTOR';
    const isManager = userInfo.role === 'manager' || userInfo.role === 'MANAGER';

    if (isDirector) return true; // Directors can edit everyone

    if (isManager) {
      // Managers can only edit florists and couriers
      const memberRole = member.role.toLowerCase();
      return memberRole === 'florist' || memberRole === 'courier';
    }

    return false;
  };

  // Shop settings edit mode functions
  const handleStartEditing = () => {
    setEditedSettings({ ...shopSettings });
    setIsEditing(true);
  };

  const handleCancelEditing = () => {
    setEditedSettings(null);
    setIsEditing(false);
    setError(null);
  };

  const validateTimeFormat = (time) => {
    if (!time) return true; // Allow empty
    const timeRegex = /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/;
    return timeRegex.test(time);
  };

  const hasUnsavedChanges = () => {
    if (!isEditing || !editedSettings || !shopSettings) return false;

    // Compare all editable fields
    return (
      editedSettings.name !== shopSettings.name ||
      editedSettings.address !== shopSettings.address ||
      editedSettings.city !== shopSettings.city ||
      editedSettings.weekday_start !== shopSettings.weekday_start ||
      editedSettings.weekday_end !== shopSettings.weekday_end ||
      editedSettings.weekend_start !== shopSettings.weekend_start ||
      editedSettings.weekend_end !== shopSettings.weekend_end ||
      editedSettings.delivery_cost !== shopSettings.delivery_cost ||
      editedSettings.free_delivery_amount !== shopSettings.free_delivery_amount ||
      editedSettings.pickup_available !== shopSettings.pickup_available ||
      editedSettings.delivery_available !== shopSettings.delivery_available
    );
  };

  const handleSaveSettings = async () => {
    if (!editedSettings) return;

    // Validate required fields
    if (!editedSettings.city) {
      setError('Пожалуйста, выберите город');
      return;
    }

    // Validate time formats
    const timeFields = [
      { field: 'weekday_start', label: 'Время открытия (будни)' },
      { field: 'weekday_end', label: 'Время закрытия (будни)' },
      { field: 'weekend_start', label: 'Время открытия (выходные)' },
      { field: 'weekend_end', label: 'Время закрытия (выходные)' }
    ];

    for (const { field, label } of timeFields) {
      if (editedSettings[field] && !validateTimeFormat(editedSettings[field])) {
        setError(`Неверный формат времени для поля "${label}". Используйте формат ЧЧ:ММ`);
        return;
      }
    }

    try {
      setIsSaving(true);
      setError(null);

      // Prepare updates grouped by endpoint
      const settingsUpdate = {};
      const workingHoursUpdate = {};
      const deliveryUpdate = {};

      // Check what changed and group updates
      if (editedSettings.name !== shopSettings.name) settingsUpdate.name = editedSettings.name;
      if (editedSettings.address !== shopSettings.address) settingsUpdate.address = editedSettings.address;
      if (editedSettings.city !== shopSettings.city) settingsUpdate.city = editedSettings.city;

      if (editedSettings.weekday_start !== shopSettings.weekday_start) workingHoursUpdate.weekday_start = editedSettings.weekday_start;
      if (editedSettings.weekday_end !== shopSettings.weekday_end) workingHoursUpdate.weekday_end = editedSettings.weekday_end;
      if (editedSettings.weekend_start !== shopSettings.weekend_start) workingHoursUpdate.weekend_start = editedSettings.weekend_start;
      if (editedSettings.weekend_end !== shopSettings.weekend_end) workingHoursUpdate.weekend_end = editedSettings.weekend_end;

      if (editedSettings.delivery_cost !== shopSettings.delivery_cost) deliveryUpdate.delivery_cost = editedSettings.delivery_cost;
      if (editedSettings.free_delivery_amount !== shopSettings.free_delivery_amount) deliveryUpdate.free_delivery_amount = editedSettings.free_delivery_amount;
      if (editedSettings.pickup_available !== shopSettings.pickup_available) deliveryUpdate.pickup_available = editedSettings.pickup_available;
      if (editedSettings.delivery_available !== shopSettings.delivery_available) deliveryUpdate.delivery_available = editedSettings.delivery_available;

      // Send updates in parallel if there are changes
      const updatePromises = [];

      if (Object.keys(settingsUpdate).length > 0) {
        updatePromises.push(shopAPI.updateShopSettings(settingsUpdate));
      }

      if (Object.keys(workingHoursUpdate).length > 0) {
        updatePromises.push(shopAPI.updateWorkingHours(workingHoursUpdate));
      }

      if (Object.keys(deliveryUpdate).length > 0) {
        updatePromises.push(shopAPI.updateDeliverySettings(deliveryUpdate));
      }

      if (updatePromises.length > 0) {
        await Promise.all(updatePromises);
      }

      // Reload shop settings to get latest data
      const shopData = await shopAPI.getShopSettings();
      setShopSettings(shopData);
      setEditedSettings(null);
      setIsEditing(false);

      // Show success message briefly
      setError(null);
      setSuccessMessage('Настройки успешно сохранены');
      setTimeout(() => setSuccessMessage(null), 3000);

    } catch (err) {
      console.error('Error saving shop settings:', err);
      setSuccessMessage(null);

      // Determine error type
      if (err.message?.includes('Failed to fetch') || err.message?.includes('Network')) {
        setErrorType('network');
        setError('Проверьте интернет-соединение');
      } else if (err.message?.includes('400') || err.message?.includes('валидац')) {
        setErrorType('validation');
        setError(err.message);
      } else {
        setErrorType(null);
        setError(err.message || 'Произошла ошибка при сохранении');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setErrorType(null);
    handleSaveSettings();
  };

  const updateLocalSetting = (field, value) => {
    setEditedSettings(prev => ({
      ...prev,
      [field]: value
    }));
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

  // Determine which settings to display (editing or saved)
  const currentSettings = isEditing ? (editedSettings || shopSettings) : shopSettings;

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
                <div className="flex gap-2 mt-2">
                  {errorType === 'network' && (
                    <button
                      onClick={handleRetry}
                      className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
                    >
                      Повторить
                    </button>
                  )}
                  <button
                    onClick={() => { setError(null); setErrorType(null); }}
                    className="text-red-500 text-xs underline"
                  >
                    Закрыть
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Display */}
      {successMessage && (
        <div className="px-4 mt-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-green-700 text-sm font-medium">{successMessage}</p>
            </div>
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
                  {userInfo.role === 'director' || userInfo.role === 'DIRECTOR' ? 'Директор' :
                   userInfo.role === 'manager' || userInfo.role === 'MANAGER' ? 'Менеджер' :
                   userInfo.role === 'florist' || userInfo.role === 'FLORIST' ? 'Флорист' :
                   userInfo.role === 'courier' || userInfo.role === 'COURIER' ? 'Курьер' : userInfo.role}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Team Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-['Open_Sans'] font-semibold">Команда</h2>
            {userInfo && (userInfo.role === 'director' || userInfo.role === 'DIRECTOR' || userInfo.role === 'manager' || userInfo.role === 'MANAGER') && (
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
                {editingMemberId === member.id ? (
                  // Edit mode
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <h4 className="text-sm font-['Open_Sans'] font-semibold">{member.name}</h4>
                        <p className="text-xs text-gray-disabled">{member.phone}</p>
                      </div>
                      <select
                        value={editedRole}
                        onChange={(e) => setEditedRole(e.target.value)}
                        className="text-xs px-3 py-1.5 rounded border border-gray-border bg-white min-w-[100px]"
                        disabled={updateLoading || deleteLoading}
                      >
                        <option value="manager">Менеджер</option>
                        <option value="florist">Флорист</option>
                        <option value="courier">Курьер</option>
                        {(userInfo?.role === 'director' || userInfo?.role === 'DIRECTOR') && (
                          <option value="director">Директор</option>
                        )}
                      </select>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleUpdateRole(member.id)}
                        disabled={updateLoading || deleteLoading || editedRole === member.role}
                        className="flex-1 px-2 py-1 bg-green-success text-white text-xs rounded disabled:opacity-50"
                      >
                        {updateLoading ? 'Сохранение...' : 'Сохранить'}
                      </button>
                      <button
                        onClick={() => handleDeleteMember(member.id, member.name)}
                        disabled={updateLoading || deleteLoading}
                        className="flex-1 px-2 py-1 bg-red-500 text-white text-xs rounded disabled:opacity-50"
                      >
                        {deleteLoading ? 'Удаление...' : 'Удалить'}
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        disabled={updateLoading || deleteLoading}
                        className="flex-1 px-2 py-1 bg-gray-neutral text-gray-disabled text-xs rounded disabled:opacity-50"
                      >
                        Отмена
                      </button>
                    </div>
                  </div>
                ) : (
                  // View mode
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="text-sm font-['Open_Sans'] font-semibold">{member.name}</h4>
                      <p className="text-xs text-gray-disabled">{member.phone}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs bg-white px-2 py-1 rounded text-gray-disabled">
                        {member.role === 'director' || member.role === 'DIRECTOR' ? 'Директор' :
                         member.role === 'manager' || member.role === 'MANAGER' ? 'Менеджер' :
                         member.role === 'florist' || member.role === 'FLORIST' ? 'Флорист' :
                         member.role === 'courier' || member.role === 'COURIER' ? 'Курьер' : member.role}
                      </span>
                      {canEditMember(member) && (
                        <button
                          onClick={() => handleEditMember(member)}
                          className="p-1 hover:bg-gray-100 rounded transition-colors"
                          title="Редактировать"
                        >
                          <svg
                            width="16"
                            height="16"
                            viewBox="0 0 16 16"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                            className="text-gray-disabled hover:text-purple-primary"
                          >
                            <path
                              d="M11.334 2.00004C11.5091 1.82494 11.7169 1.68605 11.9457 1.59129C12.1745 1.49653 12.4197 1.44775 12.6674 1.44775C12.915 1.44775 13.1602 1.49653 13.389 1.59129C13.6178 1.68605 13.8256 1.82494 14.0007 2.00004C14.1757 2.17513 14.3146 2.383 14.4094 2.61178C14.5042 2.84055 14.5529 3.08575 14.5529 3.33337C14.5529 3.58099 14.5042 3.82619 14.4094 4.05497C14.3146 4.28374 14.1757 4.49161 14.0007 4.66671L5.00065 13.6667L1.33398 14.6667L2.33398 11L11.334 2.00004Z"
                              stroke="currentColor"
                              strokeWidth="1.33333"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Pending Invitations Section */}
        {teamInvitations && teamInvitations.filter(inv => inv.status === 'pending').length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-['Open_Sans'] font-semibold mb-4">Отправленные приглашения</h2>
            <div className="space-y-3">
              {teamInvitations
                .filter(inv => inv.status === 'pending')
                .map((invitation) => (
                  <div key={invitation.id} className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="text-sm font-['Open_Sans'] font-semibold">{invitation.name}</h4>
                        <p className="text-xs text-gray-disabled">{invitation.phone}</p>
                        <p className="text-xs text-gray-disabled">
                          Роль: {invitation.role === 'director' || invitation.role === 'DIRECTOR' ? 'Директор' :
                                invitation.role === 'manager' || invitation.role === 'MANAGER' ? 'Менеджер' :
                                invitation.role === 'florist' || invitation.role === 'FLORIST' ? 'Флорист' :
                                invitation.role === 'courier' || invitation.role === 'COURIER' ? 'Курьер' : invitation.role}
                        </p>
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-xs font-semibold bg-amber-100 px-2 py-1 rounded">
                            Код: {invitation.invitation_code}
                          </span>
                          <span className="text-xs text-amber-700">
                            Ожидает принятия
                          </span>
                        </div>
                        {invitation.expires_at && (
                          <p className="text-xs text-gray-disabled mt-1">
                            Действует до: {new Date(invitation.expires_at).toLocaleDateString('ru-RU')}
                          </p>
                        )}
                      </div>
                      {userInfo && (userInfo.role === 'director' || userInfo.role === 'DIRECTOR' || userInfo.role === 'manager' || userInfo.role === 'MANAGER') && (
                        <button
                          onClick={() => handleCancelInvitation(invitation.id)}
                          className="px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded transition-colors"
                          title="Отменить приглашение"
                        >
                          Отменить
                        </button>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Shop Settings */}
        {shopSettings && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-['Open_Sans'] font-semibold">Настройки магазина</h2>
              {!isEditing ? (
                <button
                  onClick={handleStartEditing}
                  className="px-3 py-1 bg-purple-primary text-white text-sm rounded-md"
                >
                  Редактировать
                </button>
              ) : (
                <div className="flex gap-2 items-center">
                  {hasUnsavedChanges() && (
                    <div className="flex items-center gap-1 text-xs text-amber-600">
                      <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                      <span>Несохраненные изменения</span>
                    </div>
                  )}
                  <button
                    onClick={handleCancelEditing}
                    disabled={isSaving}
                    className="px-3 py-1 text-sm text-gray-disabled border border-gray-neutral rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={handleSaveSettings}
                    disabled={isSaving}
                    className="px-3 py-1 bg-green-success text-white text-sm rounded-md disabled:opacity-50"
                  >
                    {isSaving ? 'Сохранение...' : 'Сохранить'}
                  </button>
                </div>
              )}
            </div>

            {/* New shop hint */}
            {!shopSettings.address && !shopSettings.city && shopSettings.name === 'Мой магазин' && !isEditing && (
              <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm text-blue-800 font-semibold mb-1">Заполните данные вашего магазина</p>
                    <p className="text-xs text-blue-700">
                      Пожалуйста, нажмите "Редактировать" и укажите название, адрес и город вашего магазина. Эти данные будут отображаться клиентам.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Shop Name */}
            <div className="mb-4">
              <label className="block text-sm text-gray-disabled mb-2">Название магазина</label>
              <input
                type="text"
                value={currentSettings?.name || ''}
                onChange={(e) => updateLocalSetting('name', e.target.value)}
                disabled={!isEditing}
                className="w-full px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                placeholder="Введите название магазина"
              />
            </div>

            {/* Address */}
            <div className="mb-4">
              <label className="block text-sm text-gray-disabled mb-2">Адрес</label>
              <input
                type="text"
                value={currentSettings?.address || ''}
                onChange={(e) => updateLocalSetting('address', e.target.value)}
                disabled={!isEditing}
                className="w-full px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                placeholder="Введите адрес магазина"
              />
            </div>

            {/* City */}
            <div className="mb-4">
              <label className="block text-sm text-gray-disabled mb-2">
                Город {isEditing && <span className="text-red-500">*</span>}
              </label>
              <select
                value={currentSettings?.city || ''}
                onChange={(e) => updateLocalSetting('city', e.target.value)}
                disabled={!isEditing}
                className="w-full px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <option value="">Выберите город</option>
                <option value="Almaty">Алматы</option>
                <option value="Astana">Астана</option>
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
                    value={currentSettings?.weekday_start || '09:00'}
                    onChange={(e) => updateLocalSetting('weekday_start', e.target.value)}
                    disabled={!isEditing}
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  <input
                    type="time"
                    value={currentSettings?.weekday_end || '18:00'}
                    onChange={(e) => updateLocalSetting('weekday_end', e.target.value)}
                    disabled={!isEditing}
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
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
                    value={currentSettings?.weekend_start || '10:00'}
                    onChange={(e) => updateLocalSetting('weekend_start', e.target.value)}
                    disabled={!isEditing}
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  <input
                    type="time"
                    value={currentSettings?.weekend_end || '17:00'}
                    onChange={(e) => updateLocalSetting('weekend_end', e.target.value)}
                    disabled={!isEditing}
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    className="flex-1 px-3 py-2 bg-gray-input rounded-md text-sm disabled:opacity-60 disabled:cursor-not-allowed"
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
                      value={Math.floor((currentSettings?.delivery_cost || 0) / 100)}
                      onChange={(e) => updateLocalSetting('delivery_cost', (parseInt(e.target.value) || 0) * 100)}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 bg-gray-input rounded-md text-sm pr-8 disabled:opacity-60 disabled:cursor-not-allowed"
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
                      value={Math.floor((currentSettings?.free_delivery_amount || 0) / 100)}
                      onChange={(e) => updateLocalSetting('free_delivery_amount', (parseInt(e.target.value) || 0) * 100)}
                      disabled={!isEditing}
                      className="w-full px-3 py-2 bg-gray-input rounded-md text-sm pr-8 disabled:opacity-60 disabled:cursor-not-allowed"
                      placeholder="0"
                    />
                    <span className="absolute right-3 top-2 text-sm text-gray-disabled">₸</span>
                  </div>
                </div>

                <div className="flex items-center justify-between py-2">
                  <span className="text-sm">Самовывоз доступен</span>
                  <ToggleSwitch
                    isEnabled={currentSettings?.pickup_available || false}
                    onToggle={(value) => updateLocalSetting('pickup_available', value)}
                    disabled={!isEditing}
                  />
                </div>

                <div className="flex items-center justify-between py-2">
                  <span className="text-sm">Доставка доступна</span>
                  <ToggleSwitch
                    isEnabled={currentSettings?.delivery_available || false}
                    onToggle={(value) => updateLocalSetting('delivery_available', value)}
                    disabled={!isEditing}
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
                  {userInfo && (userInfo.role === 'director' || userInfo.role === 'DIRECTOR') && (
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

      {/* Invitation Success Modal */}
      {showInviteSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 mx-4 w-full max-w-sm">
            <h3 className="text-lg font-['Open_Sans'] font-semibold mb-4">Приглашение отправлено!</h3>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-green-700 mb-3">
                Приглашение успешно создано. Передайте этот код новому сотруднику:
              </p>
              <div className="bg-white rounded-md p-3 text-center">
                <p className="text-2xl font-bold font-mono text-purple-primary">{invitationCode}</p>
              </div>
            </div>

            <div className="bg-gray-input rounded-lg p-3 mb-4">
              <p className="text-xs text-gray-disabled mb-2">Инструкция для нового сотрудника:</p>
              <ol className="text-xs text-gray-disabled space-y-1">
                <li>1. Перейти на страницу регистрации</li>
                <li>2. Ввести код приглашения: {invitationCode}</li>
                <li>3. Заполнить форму и создать пароль</li>
                <li>4. После регистрации сможет войти в систему</li>
              </ol>
            </div>

            <button
              onClick={() => {
                setShowInviteSuccessModal(false);
                setInvitationCode('');
              }}
              className="w-full px-4 py-2 bg-purple-primary text-white rounded-md text-sm"
            >
              Закрыть
            </button>
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