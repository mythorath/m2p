import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getAchievements, getPlayerAchievements } from '../services/api';
import { useGame } from '../context/GameContext';
import './Achievements.css';

const Achievements = () => {
  const { wallet } = useGame();

  const [allAchievements, setAllAchievements] = useState([]);
  const [playerAchievements, setPlayerAchievements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, locked, unlocked
  const [sortBy, setSortBy] = useState('ap'); // ap, name

  /**
   * Fetch achievements data
   */
  const fetchAchievements = async () => {
    setLoading(true);
    setError('');

    try {
      // Fetch all achievements
      const achievementsResult = await getAchievements();
      if (!achievementsResult.success) {
        throw new Error(achievementsResult.error);
      }

      setAllAchievements(achievementsResult.data.achievements || []);

      // Fetch player achievements if wallet is available
      if (wallet) {
        const playerResult = await getPlayerAchievements(wallet);
        if (playerResult.success) {
          setPlayerAchievements(playerResult.data.achievements || []);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch achievements');
      console.error('Achievements error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount
  useEffect(() => {
    fetchAchievements();
  }, [wallet]);

  /**
   * Check if achievement is unlocked
   */
  const isUnlocked = (achievementId) => {
    return playerAchievements.some((pa) => pa.achievement_id === achievementId);
  };

  /**
   * Get player achievement progress
   */
  const getProgress = (achievementId) => {
    const playerAch = playerAchievements.find((pa) => pa.achievement_id === achievementId);
    return playerAch?.progress || 0;
  };

  /**
   * Filter and sort achievements
   */
  const getFilteredAchievements = () => {
    let filtered = [...allAchievements];

    // Apply filter
    if (filter === 'locked') {
      filtered = filtered.filter((ach) => !isUnlocked(ach.id));
    } else if (filter === 'unlocked') {
      filtered = filtered.filter((ach) => isUnlocked(ach.id));
    }

    // Apply sort
    if (sortBy === 'ap') {
      filtered.sort((a, b) => b.ap_reward - a.ap_reward);
    } else if (sortBy === 'name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    }

    return filtered;
  };

  /**
   * Calculate progress percentage
   */
  const getProgressPercentage = (achievement) => {
    if (!achievement.stages || achievement.stages.length === 0) {
      return isUnlocked(achievement.id) ? 100 : 0;
    }

    const progress = getProgress(achievement.id);
    const totalStages = achievement.stages.length;
    return Math.min((progress / totalStages) * 100, 100);
  };

  /**
   * Get total stats
   */
  const getTotalStats = () => {
    const total = allAchievements.length;
    const unlocked = allAchievements.filter((ach) => isUnlocked(ach.id)).length;
    const totalAP = playerAchievements.reduce((sum, pa) => sum + pa.ap_earned, 0);

    return { total, unlocked, totalAP };
  };

  const stats = getTotalStats();

  return (
    <div className="achievements-container">
      <div className="achievements-header">
        <Link to="/game" className="back-link">← Back to Game</Link>
        <h1>Achievements</h1>

        {/* Stats Summary */}
        <div className="achievement-stats">
          <div className="stat-box">
            <span className="stat-value">{stats.unlocked}/{stats.total}</span>
            <span className="stat-label">Unlocked</span>
          </div>
          <div className="stat-box">
            <span className="stat-value">{stats.totalAP}</span>
            <span className="stat-label">Total AP Earned</span>
          </div>
          <div className="stat-box">
            <span className="stat-value">
              {stats.total > 0 ? Math.round((stats.unlocked / stats.total) * 100) : 0}%
            </span>
            <span className="stat-label">Completion</span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="achievements-controls">
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filter === 'unlocked' ? 'active' : ''}`}
            onClick={() => setFilter('unlocked')}
          >
            Unlocked
          </button>
          <button
            className={`filter-btn ${filter === 'locked' ? 'active' : ''}`}
            onClick={() => setFilter('locked')}
          >
            Locked
          </button>
        </div>

        <div className="sort-buttons">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="ap">AP Reward</option>
            <option value="name">Name</option>
          </select>
        </div>
      </div>

      {/* Achievements Grid */}
      <div className="achievements-content">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner">Loading achievements...</div>
          </div>
        ) : error ? (
          <div className="error-state">
            <p>{error}</p>
            <button onClick={fetchAchievements} className="btn-retry">
              Retry
            </button>
          </div>
        ) : getFilteredAchievements().length === 0 ? (
          <div className="empty-state">
            <p>No achievements found</p>
          </div>
        ) : (
          <div className="achievements-grid">
            {getFilteredAchievements().map((achievement, index) => {
              const unlocked = isUnlocked(achievement.id);
              const progressPercentage = getProgressPercentage(achievement);

              return (
                <motion.div
                  key={achievement.id}
                  className={`achievement-card ${unlocked ? 'unlocked' : 'locked'}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.03 }}
                >
                  {/* Icon */}
                  <div className="achievement-icon">
                    {achievement.icon || '🏆'}
                  </div>

                  {/* Content */}
                  <div className="achievement-content">
                    <h3 className="achievement-name">{achievement.name}</h3>
                    <p className="achievement-description">{achievement.description}</p>

                    {/* AP Reward */}
                    <div className="achievement-reward">
                      <span className="reward-icon">⚡</span>
                      <span className="reward-value">{achievement.ap_reward} AP</span>
                    </div>

                    {/* Progress Bar (for multi-stage achievements) */}
                    {achievement.stages && achievement.stages.length > 0 && (
                      <div className="achievement-progress">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${progressPercentage}%` }}
                          />
                        </div>
                        <span className="progress-text">
                          {getProgress(achievement.id)} / {achievement.stages.length}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Unlock Status */}
                  {unlocked && (
                    <div className="unlocked-badge">
                      <span>✓</span>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Achievements;
