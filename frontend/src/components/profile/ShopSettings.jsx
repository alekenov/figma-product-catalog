import React, { useState } from 'react';
import { useProfile } from './ProfileContext';
import { shopAPI } from '../../services';
import ToggleSwitch from '../ToggleSwitch';

const ShopSettings = () => {
  const { shopSettings, refreshShop, error: contextError, setError: setContextError } = useProfile();

  const [isEditing, setIsEditing] = useState(false);
  const [editedSettings, setEditedSettings] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  const [errorType, setErrorType] = useState(null); // 'network' | 'validation' | null
  const [localError, setLocalError] = useState(null);

  const handleStartEditing = () => {
    setEditedSettings({ ...shopSettings });
    setIsEditing(true);
  };

  const handleCancelEditing = () => {
    setEditedSettings(null);
    setIsEditing(false);
    setLocalError(null);
    setContextError(null);
  };

  const validateTimeFormat = (time) => {
    if (!time) return true; // Allow empty
    const timeRegex = /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/;
    return timeRegex.test(time);
  };

  const hasUnsavedChanges = () => {
    if (!isEditing || !editedSettings || !shopSettings) return false;

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
      setLocalError('Пожалуйста, выберите город');
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
        setLocalError(`Неверный формат времени для поля "${label}". Используйте формат ЧЧ:ММ`);
        return;
      }
    }

    try {
      setIsSaving(true);
      setLocalError(null);
      setContextError(null);

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
      await refreshShop();
      setEditedSettings(null);
      setIsEditing(false);

      // Show success message briefly
      setLocalError(null);
      setSuccessMessage('Настройки успешно сохранены');
      setTimeout(() => setSuccessMessage(null), 3000);

    } catch (err) {
      console.error('Error saving shop settings:', err);
      setSuccessMessage(null);

      // Determine error type
      if (err.message?.includes('Failed to fetch') || err.message?.includes('Network')) {
        setErrorType('network');
        setLocalError('Проверьте интернет-соединение');
      } else if (err.message?.includes('400') || err.message?.includes('валидац')) {
        setErrorType('validation');
        setLocalError(err.message);
      } else {
        setErrorType(null);
        setLocalError(err.message || 'Произошла ошибка при сохранении');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleRetry = () => {
    setLocalError(null);
    setErrorType(null);
    handleSaveSettings();
  };

  const updateLocalSetting = (field, value) => {
    setEditedSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (!shopSettings) return null;

  // Determine which settings to display (editing or saved)
  const currentSettings = isEditing ? (editedSettings || shopSettings) : shopSettings;
  const displayError = localError || contextError;

  return (
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

      {/* Error Display */}
      {displayError && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-red-700 text-sm">{displayError}</p>
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
                  onClick={() => { setLocalError(null); setContextError(null); setErrorType(null); }}
                  className="text-red-500 text-xs underline"
                >
                  Закрыть
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <p className="text-green-700 text-sm font-medium">{successMessage}</p>
          </div>
        </div>
      )}

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

      {/* Delivery Settings */}
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
  );
};

export default ShopSettings;
