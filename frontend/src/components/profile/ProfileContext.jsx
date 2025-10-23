import React, { createContext, useContext, useState, useEffect } from 'react';
import { profileAPI, shopAPI } from '../../services';

const ProfileContext = createContext(null);

export const ProfileProvider = ({ children }) => {
  const [profileData, setProfileData] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [teamInvitations, setTeamInvitations] = useState([]);
  const [shopSettings, setShopSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load all data on mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
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

  const refreshProfile = async () => {
    // Currently profile data comes from AuthContext
    // This method reserved for future profile-specific data
  };

  const refreshTeam = async () => {
    try {
      const [teamData, invitationsData] = await Promise.all([
        profileAPI.getTeamMembers({ limit: 50 }),
        profileAPI.getTeamInvitations()
      ]);
      setTeamMembers(teamData);
      setTeamInvitations(invitationsData || []);
    } catch (err) {
      console.error('Error refreshing team data:', err);
      setError(err.message);
    }
  };

  const refreshShop = async () => {
    try {
      const shopData = await shopAPI.getShopSettings();
      setShopSettings(shopData);
    } catch (err) {
      console.error('Error refreshing shop settings:', err);
      setError(err.message);
    }
  };

  const value = {
    profileData,
    teamMembers,
    teamInvitations,
    shopSettings,
    loading,
    error,
    refreshProfile,
    refreshTeam,
    refreshShop,
    setError
  };

  return (
    <ProfileContext.Provider value={value}>
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = () => {
  const context = useContext(ProfileContext);
  if (!context) {
    throw new Error('useProfile must be used within ProfileProvider');
  }
  return context;
};
