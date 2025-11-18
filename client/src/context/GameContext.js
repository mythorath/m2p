import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import usePlayer from '../hooks/usePlayer';
import useWebSocket from '../hooks/useWebSocket';

// Create the context
const GameContext = createContext(null);

/**
 * GameContext Provider Component
 * Manages global game state including player data, notifications, and WebSocket connection
 */
export const GameProvider = ({ children }) => {
  // Wallet and authentication
  const [wallet, setWallet] = useState(() => {
    // Load wallet from localStorage on init
    return localStorage.getItem('wallet') || null;
  });

  // Notifications
  const [notifications, setNotifications] = useState([]);
  const [showRewardPopup, setShowRewardPopup] = useState(false);
  const [rewardData, setRewardData] = useState(null);

  // Player data hook
  const {
    player,
    loading: playerLoading,
    error: playerError,
    refresh: refreshPlayer,
    updatePlayer,
    clearPlayer,
  } = usePlayer(wallet, {
    autoRefresh: false,
    onUpdate: (data) => {
      console.log('Player data updated:', data);
    },
  });

  // WebSocket hook with callbacks
  const {
    connected: socketConnected,
    miningReward,
    lastEvent,
    error: socketError,
    clearMiningReward,
  } = useWebSocket(wallet, {
    onMiningReward: (data) => {
      // Show reward popup
      setRewardData(data);
      setShowRewardPopup(true);

      // Refresh player data to get updated stats
      refreshPlayer();

      // Add notification
      addNotification({
        type: 'mining_reward',
        message: `You mined ${data.advc_amount} ADVC!`,
        data,
      });
    },
    onAchievementUnlocked: (data) => {
      // Add notification
      addNotification({
        type: 'achievement',
        message: `Achievement Unlocked: ${data.achievement_name}!`,
        data,
      });

      // Refresh player data
      refreshPlayer();
    },
    onPlayerUpdated: (data) => {
      // Update player data locally
      updatePlayer(data);
    },
  });

  /**
   * Login with wallet address
   * @param {string} walletAddress - Player's wallet address
   */
  const login = useCallback((walletAddress) => {
    setWallet(walletAddress);
    localStorage.setItem('wallet', walletAddress);
  }, []);

  /**
   * Logout and clear all data
   */
  const logout = useCallback(() => {
    setWallet(null);
    localStorage.removeItem('wallet');
    clearPlayer();
    setNotifications([]);
    setRewardData(null);
    setShowRewardPopup(false);
  }, [clearPlayer]);

  /**
   * Add a notification
   * @param {Object} notification - Notification object
   */
  const addNotification = useCallback((notification) => {
    const id = Date.now();
    const newNotification = {
      id,
      timestamp: Date.now(),
      ...notification,
    };

    setNotifications((prev) => [newNotification, ...prev].slice(0, 50)); // Keep last 50

    // Auto-remove after 10 seconds
    setTimeout(() => {
      removeNotification(id);
    }, 10000);
  }, []);

  /**
   * Remove a notification
   * @param {number} id - Notification ID
   */
  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  /**
   * Clear all notifications
   */
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  /**
   * Hide reward popup
   */
  const hideRewardPopup = useCallback(() => {
    setShowRewardPopup(false);
    clearMiningReward();
  }, [clearMiningReward]);

  // Context value
  const value = {
    // Wallet & Auth
    wallet,
    isAuthenticated: !!wallet,
    login,
    logout,

    // Player Data
    player,
    playerLoading,
    playerError,
    refreshPlayer,
    updatePlayer,

    // WebSocket
    socketConnected,
    socketError,
    lastEvent,

    // Notifications
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,

    // Reward Popup
    showRewardPopup,
    rewardData,
    hideRewardPopup,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};

/**
 * Custom hook to use the GameContext
 */
export const useGame = () => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
};

export default GameContext;
