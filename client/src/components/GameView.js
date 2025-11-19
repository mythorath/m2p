import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useGame } from '../context/GameContext';
import RewardPopup from './RewardPopup';
import './GameView.css';

const GameView = () => {
  const navigate = useNavigate();
  const {
    isAuthenticated,
    player,
    playerLoading,
    playerError,
    refreshPlayer,
    socketConnected,
    notifications,
    showRewardPopup,
    rewardData,
    hideRewardPopup,
    logout,
  } = useGame();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  // Fetch player data on mount
  useEffect(() => {
    if (isAuthenticated) {
      refreshPlayer();
    }
  }, [isAuthenticated, refreshPlayer]);

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  /**
   * Get verification status badge
   */
  const getVerificationBadge = () => {
    if (!player) return null;

    if (player.verified) {
      return <span className="badge verified">Verified ✓</span>;
    } else {
      return <span className="badge unverified">Not Verified</span>;
    }
  };

  /**
   * Get mining status text
   */
  const getMiningStatus = () => {
    if (!player) return 'Loading...';

    if (player.verified) {
      return 'Mining rewards active! Keep mining to earn ADVC and AP.';
    } else {
      return 'Please verify your wallet to start earning rewards.';
    }
  };

  if (playerLoading && !player) {
    return (
      <div className="game-view loading">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (playerError) {
    return (
      <div className="game-view error">
        <div className="error-container">
          <h2>Error Loading Player Data</h2>
          <p>{playerError}</p>
          <button onClick={refreshPlayer} className="btn-primary">
            Retry
          </button>
          <button onClick={handleLogout} className="btn-secondary">
            Logout
          </button>
        </div>
      </div>
    );
  }

  if (!player) {
    return null;
  }

  return (
    <div className="game-view">
      {/* Header */}
      <header className="game-header">
        <div className="header-left">
          <h1 className="game-title">Mine to Play</h1>
          <div className="connection-status">
            <span className={`status-dot ${socketConnected ? 'connected' : 'disconnected'}`} />
            {socketConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        <div className="header-center">
          <div className="player-info">
            <div className="player-name">{player.display_name}</div>
            {getVerificationBadge()}
          </div>
        </div>

        <div className="header-right">
          <nav className="nav-menu">
            <Link to="/dungeons" className="nav-link">🏰 Dungeons</Link>
            <Link to="/leaderboard" className="nav-link">Leaderboard</Link>
            <Link to="/achievements" className="nav-link">Achievements</Link>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <div className="game-content">
        {/* Stats Bar */}
        <div className="stats-bar">
          <div className="stat-item">
            <span className="stat-icon">💎</span>
            <div className="stat-details">
              <span className="stat-label">ADVC Mined</span>
              <span className="stat-value">{parseFloat(player.total_advc || 0).toFixed(8)}</span>
            </div>
          </div>

          <div className="stat-item">
            <span className="stat-icon">⚡</span>
            <div className="stat-details">
              <span className="stat-label">Adventure Points</span>
              <span className="stat-value">{player.total_ap || 0}</span>
            </div>
          </div>

          <div className="stat-item">
            <span className="stat-icon">🏆</span>
            <div className="stat-details">
              <span className="stat-label">Achievements</span>
              <span className="stat-value">{player.achievements_unlocked || 0}</span>
            </div>
          </div>
        </div>

        {/* Mining Scene */}
        <div className="mining-scene">
          <motion.div
            className="miner-character"
            animate={{
              rotate: [0, -5, 5, -5, 5, 0],
              y: [0, -5, 0, -5, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            ⛏️
          </motion.div>

          <div className="mining-status">
            <h2>{player.verified ? 'Mining Active' : 'Verification Required'}</h2>
            <p>{getMiningStatus()}</p>

            {!player.verified && (
              <div className="verification-reminder">
                <p>You need to verify your wallet to start earning rewards.</p>
                <p className="wallet-display">Wallet: {player.wallet_address}</p>
              </div>
            )}
          </div>

          {/* Mining Animation */}
          {player.verified && (
            <div className="ore-particles">
              {[...Array(10)].map((_, i) => (
                <motion.div
                  key={i}
                  className="ore-particle"
                  animate={{
                    y: [-20, -100],
                    opacity: [1, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: i * 0.3,
                  }}
                  style={{
                    left: `${20 + i * 8}%`,
                  }}
                >
                  ✨
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-section">
            <h3>Recent Activity</h3>
            <div className="activity-feed">
              {notifications.length === 0 ? (
                <p className="no-activity">No recent activity</p>
              ) : (
                notifications.slice(0, 10).map((notification) => (
                  <div key={notification.id} className={`activity-item ${notification.type}`}>
                    <span className="activity-icon">
                      {notification.type === 'mining_reward' ? '💎' : '🏆'}
                    </span>
                    <div className="activity-details">
                      <p className="activity-message">{notification.message}</p>
                      <span className="activity-time">
                        {new Date(notification.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Quick Stats</h3>
            <div className="quick-stats">
              <div className="quick-stat">
                <span className="quick-stat-label">Last Reward:</span>
                <span className="quick-stat-value">
                  {notifications.find(n => n.type === 'mining_reward')?.data?.advc_amount || 'N/A'}
                </span>
              </div>
              <div className="quick-stat">
                <span className="quick-stat-label">Wallet:</span>
                <span className="quick-stat-value wallet-short">
                  {player.wallet_address.slice(0, 8)}...{player.wallet_address.slice(-6)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reward Popup */}
      <RewardPopup
        show={showRewardPopup}
        data={rewardData}
        onClose={hideRewardPopup}
      />
    </div>
  );
};

export default GameView;
