import axios from 'axios';

// Configure axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for standardized error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const errorMessage = error.response?.data?.error || error.message || 'An error occurred';
    console.error('API Error:', errorMessage);
    throw new Error(errorMessage);
  }
);

/**
 * Register a new player
 * @param {string} wallet - Player's wallet address
 * @param {string} displayName - Player's display name
 * @returns {Promise<Object>} Registration response with challenge details
 */
export const registerPlayer = async (wallet, displayName) => {
  try {
    const response = await api.post('/players/register', {
      wallet,
      display_name: displayName,
    });
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get player data by wallet address
 * @param {string} wallet - Player's wallet address
 * @returns {Promise<Object>} Player data
 */
export const getPlayer = async (wallet) => {
  try {
    const response = await api.get(`/players/${wallet}`);
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Verify player's donation
 * @param {string} wallet - Player's wallet address
 * @param {string} txid - Transaction ID
 * @returns {Promise<Object>} Verification response
 */
export const verifyPlayer = async (wallet, txid) => {
  try {
    const response = await api.post('/players/verify', {
      wallet,
      txid,
    });
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get leaderboard data
 * @param {string} period - Time period ('all_time', 'week', or 'day')
 * @param {number} limit - Number of results to return
 * @returns {Promise<Object>} Leaderboard data
 */
export const getLeaderboard = async (period = 'all_time', limit = 50) => {
  try {
    const response = await api.get('/leaderboard', {
      params: { period, limit },
    });
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get all available achievements
 * @returns {Promise<Object>} Achievements list
 */
export const getAchievements = async () => {
  try {
    const response = await api.get('/achievements');
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get player's achievements
 * @param {string} wallet - Player's wallet address
 * @returns {Promise<Object>} Player's achievements
 */
export const getPlayerAchievements = async (wallet) => {
  try {
    const response = await api.get(`/players/${wallet}/achievements`);
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Spend AP on items
 * @param {string} wallet - Player's wallet address
 * @param {number} amount - Amount of AP to spend
 * @param {string} itemId - Item identifier
 * @returns {Promise<Object>} Transaction response
 */
export const spendAP = async (wallet, amount, itemId) => {
  try {
    const response = await api.post('/players/spend', {
      wallet,
      amount,
      item_id: itemId,
    });
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get global statistics
 * @returns {Promise<Object>} Global stats
 */
export const getGlobalStats = async () => {
  try {
    const response = await api.get('/stats');
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get mining pools information
 * @returns {Promise<Object>} Mining pools data
 */
export const getMiningPools = async () => {
  try {
    const response = await api.get('/pools');
    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
};

export default api;
