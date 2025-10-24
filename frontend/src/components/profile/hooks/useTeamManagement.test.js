import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTeamManagement } from './useTeamManagement';
import * as services from '../../../services';

// Mock services
vi.mock('../../../services', () => ({
  profileAPI: {
    inviteTeamMember: vi.fn(),
    changeTeamMemberRole: vi.fn(),
    removeTeamMember: vi.fn(),
    cancelInvitation: vi.fn()
  }
}));

// Mock window.confirm
global.confirm = vi.fn();

describe('useTeamManagement', () => {
  let onSuccessMock;

  beforeEach(() => {
    vi.clearAllMocks();
    onSuccessMock = vi.fn();
    global.confirm.mockReturnValue(true); // Default confirm to true
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    expect(result.current.inviteState.showModal).toBe(false);
    expect(result.current.inviteState.loading).toBe(false);
    expect(result.current.inviteState.newColleague.role).toBe('MANAGER');
    expect(result.current.editState.editingMemberId).toBe(null);
  });

  it('should open and close invite modal', () => {
    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    // Open modal
    act(() => {
      result.current.openInviteModal();
    });
    expect(result.current.inviteState.showModal).toBe(true);

    // Close modal
    act(() => {
      result.current.closeInviteModal();
    });
    expect(result.current.inviteState.showModal).toBe(false);
  });

  it('should update new colleague data', () => {
    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    act(() => {
      result.current.updateNewColleague('name', 'John Doe');
      result.current.updateNewColleague('phone', '+77001234567');
      result.current.updateNewColleague('role', 'FLORIST');
    });

    expect(result.current.inviteState.newColleague).toEqual({
      name: 'John Doe',
      phone: '+77001234567',
      role: 'FLORIST'
    });
  });

  it('should handle successful team member invitation', async () => {
    const mockInvitation = {
      invitation_code: 'ABC123',
      name: 'John Doe',
      phone: '+77001234567'
    };

    services.profileAPI.inviteTeamMember.mockResolvedValue(mockInvitation);

    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    // Set up colleague data
    act(() => {
      result.current.updateNewColleague('name', 'John Doe');
      result.current.updateNewColleague('phone', '+77001234567');
    });

    // Invite
    await act(async () => {
      await result.current.handleInvite();
    });

    expect(services.profileAPI.inviteTeamMember).toHaveBeenCalledWith({
      name: 'John Doe',
      phone: '+77001234567',
      role: 'MANAGER'
    });

    expect(result.current.inviteState.showSuccessModal).toBe(true);
    expect(result.current.inviteState.invitationCode).toBe('ABC123');
    expect(onSuccessMock).toHaveBeenCalled();
  });

  it('should throw error for incomplete invitation data', async () => {
    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    // Try to invite without data
    await expect(async () => {
      await act(async () => {
        await result.current.handleInvite();
      });
    }).rejects.toThrow('Пожалуйста, заполните все поля');
  });

  it('should handle member role edit', () => {
    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    const member = { id: 1, name: 'Jane', role: 'MANAGER' };

    act(() => {
      result.current.handleEditMember(member);
    });

    expect(result.current.editState.editingMemberId).toBe(1);
    expect(result.current.editState.editedRole).toBe('MANAGER');
  });

  it('should handle successful role update', async () => {
    services.profileAPI.changeTeamMemberRole.mockResolvedValue({});

    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    // Start editing
    act(() => {
      result.current.handleEditMember({ id: 1, name: 'Jane', role: 'MANAGER' });
      result.current.setEditedRole('FLORIST');
    });

    // Update role
    await act(async () => {
      const message = await result.current.handleUpdateRole(1, 'Jane');
      expect(message).toContain('Роль изменена');
      expect(message).toContain('Флорист');
    });

    expect(services.profileAPI.changeTeamMemberRole).toHaveBeenCalledWith(1, 'FLORIST');
    expect(result.current.editState.editingMemberId).toBe(null);
    expect(onSuccessMock).toHaveBeenCalled();
  });

  it('should handle member deletion with confirmation', async () => {
    global.confirm.mockReturnValue(true);
    services.profileAPI.removeTeamMember.mockResolvedValue({});

    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    await act(async () => {
      await result.current.handleDeleteMember(1, 'John Doe');
    });

    expect(global.confirm).toHaveBeenCalledWith('Удалить John Doe из команды?');
    expect(services.profileAPI.removeTeamMember).toHaveBeenCalledWith(1);
    expect(onSuccessMock).toHaveBeenCalled();
  });

  it('should cancel deletion if user declines confirmation', async () => {
    global.confirm.mockReturnValue(false);

    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    await act(async () => {
      await result.current.handleDeleteMember(1, 'John Doe');
    });

    expect(services.profileAPI.removeTeamMember).not.toHaveBeenCalled();
    expect(onSuccessMock).not.toHaveBeenCalled();
  });

  it('should handle invitation cancellation', async () => {
    global.confirm.mockReturnValue(true);
    services.profileAPI.cancelInvitation.mockResolvedValue({});

    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    await act(async () => {
      await result.current.handleCancelInvitation(123);
    });

    expect(global.confirm).toHaveBeenCalledWith('Отменить это приглашение?');
    expect(services.profileAPI.cancelInvitation).toHaveBeenCalledWith(123);
    expect(onSuccessMock).toHaveBeenCalled();
  });

  it('should handle API errors during invitation', async () => {
    services.profileAPI.inviteTeamMember.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useTeamManagement(onSuccessMock));

    act(() => {
      result.current.updateNewColleague('name', 'John');
      result.current.updateNewColleague('phone', '+77001234567');
    });

    await expect(async () => {
      await act(async () => {
        await result.current.handleInvite();
      });
    }).rejects.toThrow('Network error');

    expect(result.current.inviteState.loading).toBe(false);
  });
});
