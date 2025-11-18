/**
 * WebSocket Hook for M2P
 * Manages WebSocket connection and handles real-time notifications
 */
import { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const SERVER_URL = process.env.REACT_APP_SERVER_URL || 'http://localhost:5000';

export const useWebSocket = (playerId) => {
  const [isConnected, setIsConnected] = useState(false);
  const [achievementNotification, setAchievementNotification] = useState(null);
  const [miningNotification, setMiningNotification] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    // Create socket connection
    socketRef.current = io(SERVER_URL, {
      transports: ['websocket', 'polling'],
    });

    // Connection handlers
    socketRef.current.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);

      // Authenticate with player ID
      if (playerId) {
        socketRef.current.emit('authenticate', { player_id: playerId });
      }
    });

    socketRef.current.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    });

    socketRef.current.on('authenticated', (data) => {
      console.log('Authenticated:', data);
    });

    // Notification handlers
    socketRef.current.on('notification', (data) => {
      console.log('Notification received:', data);

      if (data.type === 'achievement_unlocked') {
        setAchievementNotification(data.achievement);
      } else if (data.type === 'mining_reward') {
        setMiningNotification(data);
      }
    });

    socketRef.current.on('broadcast', (data) => {
      console.log('Broadcast received:', data);
    });

    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [playerId]);

  // Clear achievement notification
  const clearAchievementNotification = () => {
    setAchievementNotification(null);
  };

  // Clear mining notification
  const clearMiningNotification = () => {
    setMiningNotification(null);
  };

  // Send a custom event
  const emit = (event, data) => {
    if (socketRef.current) {
      socketRef.current.emit(event, data);
    }
  };

  return {
    isConnected,
    achievementNotification,
    miningNotification,
    clearAchievementNotification,
    clearMiningNotification,
    emit,
  };
};
