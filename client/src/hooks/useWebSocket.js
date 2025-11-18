import { useState, useEffect, useCallback } from 'react';
import socket, { subscribeToWallet, unsubscribeFromWallet } from '../services/socket';

/**
 * Custom hook for WebSocket subscriptions
 * @param {string} wallet - Player's wallet address to subscribe to
 * @param {Object} callbacks - Event callbacks
 * @returns {Object} WebSocket state and data
 */
const useWebSocket = (wallet, callbacks = {}) => {
  const [connected, setConnected] = useState(socket.connected);
  const [miningReward, setMiningReward] = useState(null);
  const [lastEvent, setLastEvent] = useState(null);
  const [error, setError] = useState(null);

  // Handle mining reward events
  const handleMiningReward = useCallback((data) => {
    console.log('💎 Mining reward received:', data);
    setMiningReward(data);
    setLastEvent({
      type: 'mining_reward',
      data,
      timestamp: Date.now(),
    });

    // Call custom callback if provided
    if (callbacks.onMiningReward) {
      callbacks.onMiningReward(data);
    }
  }, [callbacks]);

  // Handle achievement unlocked events
  const handleAchievementUnlocked = useCallback((data) => {
    console.log('🏆 Achievement unlocked:', data);
    setLastEvent({
      type: 'achievement_unlocked',
      data,
      timestamp: Date.now(),
    });

    // Call custom callback if provided
    if (callbacks.onAchievementUnlocked) {
      callbacks.onAchievementUnlocked(data);
    }
  }, [callbacks]);

  // Handle player updated events
  const handlePlayerUpdated = useCallback((data) => {
    console.log('👤 Player updated:', data);
    setLastEvent({
      type: 'player_updated',
      data,
      timestamp: Date.now(),
    });

    // Call custom callback if provided
    if (callbacks.onPlayerUpdated) {
      callbacks.onPlayerUpdated(data);
    }
  }, [callbacks]);

  // Handle connection status changes
  const handleConnect = useCallback(() => {
    console.log('✅ WebSocket connected');
    setConnected(true);
    setError(null);

    // Resubscribe to wallet if we have one
    if (wallet) {
      subscribeToWallet(wallet);
    }

    // Call custom callback if provided
    if (callbacks.onConnect) {
      callbacks.onConnect();
    }
  }, [wallet, callbacks]);

  const handleDisconnect = useCallback((reason) => {
    console.log('❌ WebSocket disconnected:', reason);
    setConnected(false);

    // Call custom callback if provided
    if (callbacks.onDisconnect) {
      callbacks.onDisconnect(reason);
    }
  }, [callbacks]);

  const handleError = useCallback((err) => {
    console.error('WebSocket error:', err);
    setError(err);

    // Call custom callback if provided
    if (callbacks.onError) {
      callbacks.onError(err);
    }
  }, [callbacks]);

  // Set up WebSocket listeners
  useEffect(() => {
    // Connection event listeners
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connect_error', handleError);
    socket.on('error', handleError);

    // Game event listeners
    socket.on('mining_reward', handleMiningReward);
    socket.on('achievement_unlocked', handleAchievementUnlocked);
    socket.on('player_updated', handlePlayerUpdated);

    // Subscribe to wallet if provided
    if (wallet) {
      subscribeToWallet(wallet);
    }

    // Cleanup function
    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error', handleError);
      socket.off('error', handleError);
      socket.off('mining_reward', handleMiningReward);
      socket.off('achievement_unlocked', handleAchievementUnlocked);
      socket.off('player_updated', handlePlayerUpdated);

      // Unsubscribe from wallet
      if (wallet) {
        unsubscribeFromWallet(wallet);
      }
    };
  }, [
    wallet,
    handleConnect,
    handleDisconnect,
    handleError,
    handleMiningReward,
    handleAchievementUnlocked,
    handlePlayerUpdated,
  ]);

  // Clear mining reward after it's been shown
  const clearMiningReward = useCallback(() => {
    setMiningReward(null);
  }, []);

  return {
    connected,
    miningReward,
    lastEvent,
    error,
    clearMiningReward,
  };
};

export default useWebSocket;
