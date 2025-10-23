import { useState } from 'react';
import { profileAPI } from '../../../services';

export const useTeamManagement = (onSuccess) => {
  const [inviteState, setInviteState] = useState({
    showModal: false,
    showSuccessModal: false,
    invitationCode: '',
    loading: false,
    newColleague: {
      name: '',
      phone: '',
      role: 'MANAGER'
    }
  });

  const [editState, setEditState] = useState({
    editingMemberId: null,
    editedRole: '',
    updateLoading: false,
    deleteLoading: false
  });

  const openInviteModal = () => {
    setInviteState(prev => ({ ...prev, showModal: true }));
  };

  const closeInviteModal = () => {
    setInviteState(prev => ({
      ...prev,
      showModal: false,
      newColleague: { name: '', phone: '', role: 'MANAGER' }
    }));
  };

  const closeSuccessModal = () => {
    setInviteState(prev => ({
      ...prev,
      showSuccessModal: false,
      invitationCode: ''
    }));
  };

  const updateNewColleague = (field, value) => {
    setInviteState(prev => ({
      ...prev,
      newColleague: { ...prev.newColleague, [field]: value }
    }));
  };

  const handleInvite = async () => {
    const { name, phone, role } = inviteState.newColleague;

    if (!name || !phone) {
      throw new Error('Пожалуйста, заполните все поля');
    }

    try {
      setInviteState(prev => ({ ...prev, loading: true }));

      const invitation = await profileAPI.inviteTeamMember({
        name,
        phone,
        role
      });

      // Show success modal with invitation code
      setInviteState(prev => ({
        ...prev,
        showModal: false,
        showSuccessModal: true,
        invitationCode: invitation.invitation_code,
        newColleague: { name: '', phone: '', role: 'MANAGER' },
        loading: false
      }));

      // Refresh team data
      if (onSuccess) await onSuccess();

    } catch (err) {
      setInviteState(prev => ({ ...prev, loading: false }));
      throw err;
    }
  };

  const handleEditMember = (member) => {
    setEditState({
      editingMemberId: member.id,
      editedRole: member.role.toUpperCase(),
      updateLoading: false,
      deleteLoading: false
    });
  };

  const handleCancelEdit = () => {
    setEditState({
      editingMemberId: null,
      editedRole: '',
      updateLoading: false,
      deleteLoading: false
    });
  };

  const handleUpdateRole = async (userId, memberName) => {
    try {
      setEditState(prev => ({ ...prev, updateLoading: true }));

      const roleMap = {
        'DIRECTOR': 'Директор',
        'MANAGER': 'Менеджер',
        'FLORIST': 'Флорист',
        'COURIER': 'Курьер'
      };
      const newRoleDisplay = roleMap[editState.editedRole.toUpperCase()] || editState.editedRole;

      await profileAPI.changeTeamMemberRole(userId, editState.editedRole.toUpperCase());

      // Reset edit state
      setEditState({
        editingMemberId: null,
        editedRole: '',
        updateLoading: false,
        deleteLoading: false
      });

      // Refresh team data
      if (onSuccess) await onSuccess();

      return `Роль изменена: ${memberName} теперь ${newRoleDisplay}`;

    } catch (err) {
      setEditState(prev => ({ ...prev, updateLoading: false }));
      throw err;
    }
  };

  const handleDeleteMember = async (userId, memberName) => {
    if (!confirm(`Удалить ${memberName} из команды?`)) {
      return;
    }

    try {
      setEditState(prev => ({ ...prev, deleteLoading: true }));

      await profileAPI.removeTeamMember(userId);

      // Reset edit state
      setEditState({
        editingMemberId: null,
        editedRole: '',
        updateLoading: false,
        deleteLoading: false
      });

      // Refresh team data
      if (onSuccess) await onSuccess();

    } catch (err) {
      setEditState(prev => ({ ...prev, deleteLoading: false }));
      throw err;
    }
  };

  const handleCancelInvitation = async (invitationId) => {
    if (!confirm('Отменить это приглашение?')) {
      return;
    }

    try {
      await profileAPI.cancelInvitation(invitationId);

      // Refresh team data
      if (onSuccess) await onSuccess();

    } catch (err) {
      throw err;
    }
  };

  const setEditedRole = (role) => {
    setEditState(prev => ({ ...prev, editedRole: role }));
  };

  return {
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
  };
};
