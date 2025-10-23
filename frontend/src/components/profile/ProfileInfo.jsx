import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useProfile } from './ProfileContext';
import { useTeamManagement } from './hooks/useTeamManagement';

const ProfileInfo = () => {
  const { user: userInfo } = useAuth();
  const { teamMembers, teamInvitations, refreshTeam, setError } = useProfile();
  const [successMessage, setSuccessMessage] = useState(null);

  const {
    inviteState,
    editState,
    openInviteModal,
    closeInviteModal,
    closeSuccessModal,
    updateNewColleague,
    handleInvite,
    handleEditMember,
    handleCancelEdit,
    handleUpdateRole,
    handleDeleteMember,
    handleCancelInvitation,
    setEditedRole
  } = useTeamManagement(refreshTeam);

  const handleInviteSubmit = async () => {
    try {
      await handleInvite();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRoleUpdate = async (userId, memberName) => {
    try {
      const message = await handleUpdateRole(userId, memberName);
      setSuccessMessage(message);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleMemberDelete = async (userId, memberName) => {
    try {
      await handleDeleteMember(userId, memberName);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleInvitationCancel = async (invitationId) => {
    try {
      await handleCancelInvitation(invitationId);
    } catch (err) {
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

  return (
    <>
      {/* Success Message */}
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
              onClick={openInviteModal}
              className="px-3 py-1 bg-purple-primary text-white text-sm rounded-md"
            >
              Пригласить
            </button>
          )}
        </div>

        <div className="space-y-3">
          {teamMembers.map((member) => (
            <div key={member.id} className="bg-gray-input rounded-lg p-3">
              {editState.editingMemberId === member.id ? (
                // Edit mode
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="text-sm font-['Open_Sans'] font-semibold">{member.name}</h4>
                      <p className="text-xs text-gray-disabled">{member.phone}</p>
                    </div>
                    <select
                      value={editState.editedRole}
                      onChange={(e) => setEditedRole(e.target.value)}
                      className="text-xs px-3 py-1.5 rounded border border-gray-border bg-white min-w-[100px]"
                      disabled={editState.updateLoading || editState.deleteLoading}
                    >
                      <option value="MANAGER">Менеджер</option>
                      <option value="FLORIST">Флорист</option>
                      <option value="COURIER">Курьер</option>
                      {(userInfo?.role === 'director' || userInfo?.role === 'DIRECTOR') && (
                        <option value="DIRECTOR">Директор</option>
                      )}
                    </select>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleRoleUpdate(member.id, member.name)}
                      disabled={editState.updateLoading || editState.deleteLoading || editState.editedRole === member.role}
                      className="flex-1 px-2 py-1 bg-green-success text-white text-xs rounded disabled:opacity-50"
                    >
                      {editState.updateLoading ? 'Сохранение...' : 'Сохранить'}
                    </button>
                    <button
                      onClick={() => handleMemberDelete(member.id, member.name)}
                      disabled={editState.updateLoading || editState.deleteLoading}
                      className="flex-1 px-2 py-1 bg-red-500 text-white text-xs rounded disabled:opacity-50"
                    >
                      {editState.deleteLoading ? 'Удаление...' : 'Удалить'}
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      disabled={editState.updateLoading || editState.deleteLoading}
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
                        onClick={() => handleInvitationCancel(invitation.id)}
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

      {/* Invite Colleague Modal */}
      {inviteState.showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 mx-4 w-full max-w-sm">
            <h3 className="text-lg font-['Open_Sans'] font-semibold mb-4">Пригласить коллегу</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-disabled mb-2">Имя</label>
                <input
                  type="text"
                  value={inviteState.newColleague.name}
                  onChange={(e) => updateNewColleague('name', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  placeholder="Введите имя"
                  disabled={inviteState.loading}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-disabled mb-2">Телефон</label>
                <input
                  type="tel"
                  value={inviteState.newColleague.phone}
                  onChange={(e) => updateNewColleague('phone', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  placeholder="+7 (___) ___ __ __"
                  disabled={inviteState.loading}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-disabled mb-2">Роль</label>
                <select
                  value={inviteState.newColleague.role}
                  onChange={(e) => updateNewColleague('role', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-input rounded-md text-sm"
                  disabled={inviteState.loading}
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
                onClick={closeInviteModal}
                className="flex-1 px-4 py-2 text-gray-disabled border border-gray-neutral rounded-md text-sm"
                disabled={inviteState.loading}
              >
                Отмена
              </button>
              <button
                onClick={handleInviteSubmit}
                className="flex-1 px-4 py-2 bg-purple-primary text-white rounded-md text-sm disabled:opacity-50"
                disabled={inviteState.loading}
              >
                {inviteState.loading ? 'Отправка...' : 'Пригласить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invitation Success Modal */}
      {inviteState.showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 mx-4 w-full max-w-sm">
            <h3 className="text-lg font-['Open_Sans'] font-semibold mb-4">Приглашение отправлено!</h3>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-green-700 mb-3">
                Приглашение успешно создано. Передайте этот код новому сотруднику:
              </p>
              <div className="bg-white rounded-md p-3 text-center">
                <p className="text-2xl font-bold font-mono text-purple-primary">{inviteState.invitationCode}</p>
              </div>
            </div>

            <div className="bg-gray-input rounded-lg p-3 mb-4">
              <p className="text-xs text-gray-disabled mb-2">Инструкция для нового сотрудника:</p>
              <ol className="text-xs text-gray-disabled space-y-1">
                <li>1. Перейти на страницу регистрации</li>
                <li>2. Ввести код приглашения: {inviteState.invitationCode}</li>
                <li>3. Заполнить форму и создать пароль</li>
                <li>4. После регистрации сможет войти в систему</li>
              </ol>
            </div>

            <button
              onClick={closeSuccessModal}
              className="w-full px-4 py-2 bg-purple-primary text-white rounded-md text-sm"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ProfileInfo;
