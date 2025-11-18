import { useState, useEffect, useCallback } from 'react';
import { getPlayer } from '../services/api';

/**
 * Custom hook for fetching and managing player data
 * @param {string} wallet - Player's wallet address
 * @param {Object} options - Hook options
 * @returns {Object} Player state and methods
 */
const usePlayer = (wallet, options = {}) => {
  const {
    autoRefresh = false,
    refreshInterval = 30000, // 30 seconds default
    onUpdate = null,
  } = options;

  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  /**
   * Fetch player data from API
   */
  const fetchPlayer = useCallback(async () => {
    if (!wallet) {
      setPlayer(null);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await getPlayer(wallet);

      if (result.success) {
        setPlayer(result.data);
        setLastUpdated(Date.now());

        // Call custom update callback if provided
        if (onUpdate) {
          onUpdate(result.data);
        }
      } else {
        setError(result.error);
        setPlayer(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch player data');
      setPlayer(null);
    } finally {
      setLoading(false);
    }
  }, [wallet, onUpdate]);

  /**
   * Refresh player data manually
   */
  const refresh = useCallback(() => {
    return fetchPlayer();
  }, [fetchPlayer]);

  /**
   * Update player data locally (optimistic updates)
   * @param {Object} updates - Partial player data to update
   */
  const updatePlayer = useCallback((updates) => {
    setPlayer((prev) => {
      if (!prev) return null;
      return { ...prev, ...updates };
    });
  }, []);

  /**
   * Clear player data
   */
  const clearPlayer = useCallback(() => {
    setPlayer(null);
    setError(null);
    setLastUpdated(null);
  }, []);

  // Initial fetch when wallet changes
  useEffect(() => {
    fetchPlayer();
  }, [fetchPlayer]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (!autoRefresh || !wallet) {
      return;
    }

    const intervalId = setInterval(() => {
      fetchPlayer();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [autoRefresh, wallet, refreshInterval, fetchPlayer]);

  return {
    player,
    loading,
    error,
    lastUpdated,
    refresh,
    updatePlayer,
    clearPlayer,
  };
};

export default usePlayer;
