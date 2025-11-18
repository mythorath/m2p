/**
 * Leaderboard API client
 */
import axios from 'axios';
import type { LeaderboardResponse, PlayerRankResponse, LeaderboardPeriod } from '../types/leaderboard';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const leaderboardAPI = {
  /**
   * Get available leaderboard periods
   */
  getPeriods: async (): Promise<string[]> => {
    const response = await api.get('/api/leaderboard/periods');
    return response.data;
  },

  /**
   * Get leaderboard for a specific period
   */
  getLeaderboard: async (
    period: LeaderboardPeriod,
    limit: number = 100,
    offset: number = 0,
    useCache: boolean = true
  ): Promise<LeaderboardResponse> => {
    const response = await api.get(`/api/leaderboard/${period}`, {
      params: { limit, offset, use_cache: useCache },
    });
    return response.data;
  },

  /**
   * Get player's rank and nearby rankings
   */
  getPlayerRank: async (
    period: LeaderboardPeriod,
    walletAddress: string,
    context: number = 5
  ): Promise<PlayerRankResponse> => {
    const response = await api.get(`/api/leaderboard/${period}/player/${walletAddress}`, {
      params: { context },
    });
    return response.data;
  },

  /**
   * Manually refresh leaderboard cache
   */
  refreshLeaderboard: async (period: LeaderboardPeriod): Promise<void> => {
    await api.post(`/api/leaderboard/${period}/refresh`);
  },

  /**
   * Refresh all leaderboard caches
   */
  refreshAll: async (): Promise<void> => {
    await api.post('/api/leaderboard/refresh-all');
  },
};

export default leaderboardAPI;
