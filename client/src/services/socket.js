import { io } from 'socket.io-client';

// WebSocket server URL
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';

// Initialize Socket.io connection
const socket = io(SOCKET_URL, {
  autoConnect: true,
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: Infinity,
  transports: ['websocket', 'polling'],
});

// Connection event handlers
socket.on('connect', () => {
  console.log('✅ Connected to WebSocket server');
  console.log('Socket ID:', socket.id);
});

socket.on('disconnect', (reason) => {
  console.log('❌ Disconnected from WebSocket server:', reason);
  if (reason === 'io server disconnect') {
    // Server disconnected the socket, reconnect manually
    socket.connect();
  }
});

socket.on('connect_error', (error) => {
  console.error('WebSocket connection error:', error.message);
});

socket.on('reconnect', (attemptNumber) => {
  console.log(`✅ Reconnected to WebSocket server (attempt ${attemptNumber})`);
});

socket.on('reconnect_attempt', (attemptNumber) => {
  console.log(`🔄 Attempting to reconnect... (attempt ${attemptNumber})`);
});

socket.on('reconnect_error', (error) => {
  console.error('Reconnection error:', error.message);
});

socket.on('reconnect_failed', () => {
  console.error('❌ Failed to reconnect to WebSocket server');
});

// Generic error handler
socket.on('error', (error) => {
  console.error('Socket error:', error);
});

/**
 * Subscribe to a player's wallet for mining rewards
 * @param {string} wallet - Player's wallet address
 */
export const subscribeToWallet = (wallet) => {
  if (wallet) {
    socket.emit('subscribe_wallet', { wallet });
    console.log(`📡 Subscribed to wallet: ${wallet}`);
  }
};

/**
 * Unsubscribe from a player's wallet
 * @param {string} wallet - Player's wallet address
 */
export const unsubscribeFromWallet = (wallet) => {
  if (wallet) {
    socket.emit('unsubscribe_wallet', { wallet });
    console.log(`📡 Unsubscribed from wallet: ${wallet}`);
  }
};

/**
 * Get current socket connection status
 * @returns {boolean} Connection status
 */
export const isConnected = () => {
  return socket.connected;
};

/**
 * Manually connect the socket
 */
export const connect = () => {
  if (!socket.connected) {
    socket.connect();
  }
};

/**
 * Manually disconnect the socket
 */
export const disconnect = () => {
  if (socket.connected) {
    socket.disconnect();
  }
};

export default socket;
