import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getGlobalStats } from '../services/api';
import { useGame } from '../context/GameContext';
import './Stats.css';

const Stats = () => {
  const { player } = useGame();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Fetch global statistics
   */
  const fetchStats = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await getGlobalStats();

      if (result.success) {
        setStats(result.data);
      } else {
        setError(result.error || 'Failed to fetch statistics');
      }
    } catch (err) {
      setError('Failed to fetch statistics');
      console.error('Stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount
  useEffect(() => {
    fetchStats();

    // Auto-refresh every 30 seconds
    const intervalId = setInterval(() => {
      fetchStats();
    }, 30000);

    return () => clearInterval(intervalId);
  }, []);

  /**
   * Calculate player's contribution percentage
   */
  const getContributionPercentage = () => {
    if (!player || !stats) return 0;

    const totalADVC = parseFloat(stats.total_advc || 0);
    const playerADVC = parseFloat(player.total_advc || 0);

    if (totalADVC === 0) return 0;

    return ((playerADVC / totalADVC) * 100).toFixed(4);
  };

  /**
   * Format large numbers
   */
  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  /**
   * Format ADVC amount
   */
  const formatADVC = (amount) => {
    return parseFloat(amount || 0).toFixed(8);
  };

  if (loading && !stats) {
    return (
      <div className="stats-container loading">
        <div className="loading-spinner">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-container error">
        <div className="error-container">
          <h2>Error Loading Statistics</h2>
          <p>{error}</p>
          <button onClick={fetchStats} className="btn-retry">
            Retry
          </button>
          <Link to="/game" className="btn-back">
            Back to Game
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="stats-container">
      <div className="stats-header">
        <Link to="/game" className="back-link">← Back to Game</Link>
        <h1>Global Statistics</h1>
        <p className="stats-subtitle">Real-time statistics from the Mine to Play network</p>
      </div>

      <div className="stats-content">
        {/* Global Stats Grid */}
        <div className="stats-grid">
          <motion.div
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="stat-icon">👥</div>
            <div className="stat-info">
              <h3>Total Players</h3>
              <p className="stat-value">{formatNumber(stats?.total_players || 0)}</p>
              <span className="stat-label">Registered players</span>
            </div>
          </motion.div>

          <motion.div
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="stat-icon">✅</div>
            <div className="stat-info">
              <h3>Verified Players</h3>
              <p className="stat-value">{formatNumber(stats?.verified_players || 0)}</p>
              <span className="stat-label">Active miners</span>
            </div>
          </motion.div>

          <motion.div
            className="stat-card highlight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="stat-icon">💎</div>
            <div className="stat-info">
              <h3>Total ADVC Mined</h3>
              <p className="stat-value advc">{formatADVC(stats?.total_advc || 0)}</p>
              <span className="stat-label">Across all players</span>
            </div>
          </motion.div>

          <motion.div
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="stat-icon">⚡</div>
            <div className="stat-info">
              <h3>Total AP</h3>
              <p className="stat-value ap">{formatNumber(stats?.total_ap || 0)}</p>
              <span className="stat-label">Adventure points</span>
            </div>
          </motion.div>

          <motion.div
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="stat-icon">🔥</div>
            <div className="stat-info">
              <h3>Mining Events (24h)</h3>
              <p className="stat-value">{formatNumber(stats?.mining_events_24h || 0)}</p>
              <span className="stat-label">Rewards distributed</span>
            </div>
          </motion.div>

          <motion.div
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <div className="stat-icon">🏆</div>
            <div className="stat-info">
              <h3>Achievements Unlocked</h3>
              <p className="stat-value">{formatNumber(stats?.total_achievements_unlocked || 0)}</p>
              <span className="stat-label">Total unlocks</span>
            </div>
          </motion.div>
        </div>

        {/* Player Contribution Section */}
        {player && (
          <motion.div
            className="contribution-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <h2>Your Contribution</h2>
            <div className="contribution-content">
              <div className="contribution-stat">
                <span className="contribution-label">Your ADVC:</span>
                <span className="contribution-value">
                  {formatADVC(player.total_advc || 0)}
                </span>
              </div>

              <div className="contribution-stat">
                <span className="contribution-label">Network ADVC:</span>
                <span className="contribution-value">
                  {formatADVC(stats?.total_advc || 0)}
                </span>
              </div>

              <div className="contribution-stat highlight">
                <span className="contribution-label">Your Contribution:</span>
                <span className="contribution-value percentage">
                  {getContributionPercentage()}%
                </span>
              </div>

              <div className="contribution-bar">
                <div
                  className="contribution-fill"
                  style={{ width: `${Math.min(getContributionPercentage(), 100)}%` }}
                />
              </div>

              <div className="contribution-message">
                <p>
                  You've contributed {getContributionPercentage()}% of the total ADVC mined
                  across the entire network!
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Additional Info */}
        <motion.div
          className="info-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <h2>How It Works</h2>
          <div className="info-grid">
            <div className="info-item">
              <div className="info-number">1</div>
              <h3>Mine Dogecoin</h3>
              <p>
                Mine Dogecoin with any participating pool that supports the Mine to Play
                protocol.
              </p>
            </div>

            <div className="info-item">
              <div className="info-number">2</div>
              <h3>Earn ADVC</h3>
              <p>
                Automatically receive ADVC (Adventure Coin) rewards based on your mining
                contributions.
              </p>
            </div>

            <div className="info-item">
              <div className="info-number">3</div>
              <h3>Gain Adventure Points</h3>
              <p>
                Earn AP with every mining reward and unlock achievements to boost your
                standing.
              </p>
            </div>

            <div className="info-item">
              <div className="info-number">4</div>
              <h3>Compete & Progress</h3>
              <p>
                Climb the leaderboards, complete challenges, and unlock exclusive rewards.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Stats;
