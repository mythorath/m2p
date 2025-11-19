import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getLeaderboard } from '../services/api';
import { useGame } from '../context/GameContext';
import './Leaderboard.css';

const Leaderboard = () => {
  const { wallet } = useGame();

  const [period, setPeriod] = useState('all_time');
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [lastUpdated, setLastUpdated] = useState(null);

  const itemsPerPage = 50;

  /**
   * Fetch leaderboard data
   */
  const fetchLeaderboard = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await getLeaderboard(period, 1000); // Fetch more for pagination

      if (result.success) {
        setLeaderboardData(result.data.leaderboard || []);
        setLastUpdated(Date.now());
      } else {
        setError(result.error || 'Failed to fetch leaderboard');
      }
    } catch (err) {
      setError('Failed to fetch leaderboard');
      console.error('Leaderboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount and when period changes
  useEffect(() => {
    fetchLeaderboard();
  }, [period]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchLeaderboard();
    }, 30000);

    return () => clearInterval(intervalId);
  }, [period]);

  /**
   * Handle period change
   */
  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    setCurrentPage(1);
  };

  /**
   * Get paginated data
   */
  const getPaginatedData = () => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return leaderboardData.slice(startIndex, endIndex);
  };

  /**
   * Get total pages
   */
  const getTotalPages = () => {
    return Math.ceil(leaderboardData.length / itemsPerPage);
  };

  /**
   * Handle page change
   */
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  /**
   * Format number with commas
   */
  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  /**
   * Get rank medal
   */
  const getRankMedal = (rank) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return rank;
    }
  };

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <Link to="/game" className="back-link">← Back to Game</Link>
        <h1>Leaderboard</h1>
        {lastUpdated && (
          <p className="last-updated">
            Last updated: {new Date(lastUpdated).toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Period Tabs */}
      <div className="period-tabs">
        <button
          className={`tab ${period === 'all_time' ? 'active' : ''}`}
          onClick={() => handlePeriodChange('all_time')}
        >
          All-Time
        </button>
        <button
          className={`tab ${period === 'week' ? 'active' : ''}`}
          onClick={() => handlePeriodChange('week')}
        >
          This Week
        </button>
        <button
          className={`tab ${period === 'day' ? 'active' : ''}`}
          onClick={() => handlePeriodChange('day')}
        >
          Today
        </button>
      </div>

      {/* Leaderboard Table */}
      <div className="leaderboard-content">
        {loading && leaderboardData.length === 0 ? (
          <div className="loading-state">
            <div className="loading-spinner">Loading leaderboard...</div>
          </div>
        ) : error ? (
          <div className="error-state">
            <p>{error}</p>
            <button onClick={fetchLeaderboard} className="btn-retry">
              Retry
            </button>
          </div>
        ) : leaderboardData.length === 0 ? (
          <div className="empty-state">
            <p>No data available for this period</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th>ADVC Mined</th>
                    <th>Total AP</th>
                  </tr>
                </thead>
                <tbody>
                  {getPaginatedData().map((player, index) => {
                    const rank = (currentPage - 1) * itemsPerPage + index + 1;
                    const isCurrentPlayer = player.wallet_address === wallet;

                    return (
                      <motion.tr
                        key={player.wallet_address}
                        className={isCurrentPlayer ? 'current-player' : ''}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.02 }}
                      >
                        <td className="rank-cell">
                          <span className="rank">{getRankMedal(rank)}</span>
                        </td>
                        <td className="player-cell">
                          <span className="display-name">{player.display_name}</span>
                          {player.verified && <span className="verified-badge">✓</span>}
                          {isCurrentPlayer && <span className="you-badge">YOU</span>}
                        </td>
                        <td className="advc-cell">
                          <span className="advc-value">
                            {parseFloat(player.total_advc || 0).toFixed(8)}
                          </span>
                        </td>
                        <td className="ap-cell">
                          <span className="ap-value">{formatNumber(player.total_ap || 0)}</span>
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {getTotalPages() > 1 && (
              <div className="pagination">
                <button
                  className="page-btn"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </button>

                <div className="page-numbers">
                  {[...Array(getTotalPages())].map((_, i) => {
                    const pageNum = i + 1;
                    // Show first 3, last 3, and current +/- 1
                    if (
                      pageNum <= 3 ||
                      pageNum > getTotalPages() - 3 ||
                      Math.abs(pageNum - currentPage) <= 1
                    ) {
                      return (
                        <button
                          key={pageNum}
                          className={`page-num ${currentPage === pageNum ? 'active' : ''}`}
                          onClick={() => handlePageChange(pageNum)}
                        >
                          {pageNum}
                        </button>
                      );
                    } else if (
                      pageNum === 4 && currentPage > 5 ||
                      pageNum === getTotalPages() - 3 && currentPage < getTotalPages() - 4
                    ) {
                      return <span key={pageNum} className="page-ellipsis">...</span>;
                    }
                    return null;
                  })}
                </div>

                <button
                  className="page-btn"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === getTotalPages()}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
