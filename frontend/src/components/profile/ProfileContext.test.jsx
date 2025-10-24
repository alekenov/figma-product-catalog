import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ProfileProvider, useProfile } from './ProfileContext';
import * as services from '../../services';

// Mock services
vi.mock('../../services', () => ({
  profileAPI: {
    getTeamMembers: vi.fn(),
    getTeamInvitations: vi.fn()
  },
  shopAPI: {
    getShopSettings: vi.fn()
  }
}));

// Test component that uses the context
const TestComponent = () => {
  const { profileData, teamMembers, teamInvitations, shopSettings, loading, error } = useProfile();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <div data-testid="team-count">{teamMembers.length}</div>
      <div data-testid="invitations-count">{teamInvitations.length}</div>
      <div data-testid="shop-name">{shopSettings?.name}</div>
    </div>
  );
};

describe('ProfileContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should provide loading state initially', () => {
    services.profileAPI.getTeamMembers.mockResolvedValue([]);
    services.profileAPI.getTeamInvitations.mockResolvedValue([]);
    services.shopAPI.getShopSettings.mockResolvedValue({ name: 'Test Shop' });

    render(
      <ProfileProvider>
        <TestComponent />
      </ProfileProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should load profile data successfully', async () => {
    const mockTeamMembers = [
      { id: 1, name: 'John', role: 'DIRECTOR' },
      { id: 2, name: 'Jane', role: 'MANAGER' }
    ];
    const mockInvitations = [
      { id: 1, name: 'Bob', status: 'pending' }
    ];
    const mockShopSettings = { name: 'My Flower Shop', city: 'Almaty' };

    services.profileAPI.getTeamMembers.mockResolvedValue(mockTeamMembers);
    services.profileAPI.getTeamInvitations.mockResolvedValue(mockInvitations);
    services.shopAPI.getShopSettings.mockResolvedValue(mockShopSettings);

    render(
      <ProfileProvider>
        <TestComponent />
      </ProfileProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('team-count')).toHaveTextContent('2');
      expect(screen.getByTestId('invitations-count')).toHaveTextContent('1');
      expect(screen.getByTestId('shop-name')).toHaveTextContent('My Flower Shop');
    });
  });

  it('should handle API errors gracefully', async () => {
    services.profileAPI.getTeamMembers.mockRejectedValue(new Error('API Error'));
    services.profileAPI.getTeamInvitations.mockResolvedValue([]);
    services.shopAPI.getShopSettings.mockResolvedValue({});

    render(
      <ProfileProvider>
        <TestComponent />
      </ProfileProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error: API Error/)).toBeInTheDocument();
    });
  });

  it('should fetch data in parallel for performance', async () => {
    const mockTeamMembers = [];
    const mockInvitations = [];
    const mockShopSettings = { name: 'Test' };

    services.profileAPI.getTeamMembers.mockResolvedValue(mockTeamMembers);
    services.profileAPI.getTeamInvitations.mockResolvedValue(mockInvitations);
    services.shopAPI.getShopSettings.mockResolvedValue(mockShopSettings);

    render(
      <ProfileProvider>
        <TestComponent />
      </ProfileProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('shop-name')).toBeInTheDocument();
    });

    // All three API calls should have been made
    expect(services.profileAPI.getTeamMembers).toHaveBeenCalledTimes(1);
    expect(services.profileAPI.getTeamInvitations).toHaveBeenCalledTimes(1);
    expect(services.shopAPI.getShopSettings).toHaveBeenCalledTimes(1);
  });

  it('should throw error when useProfile is used outside provider', () => {
    // Suppress console.error for this test
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useProfile must be used within ProfileProvider');

    spy.mockRestore();
  });
});
