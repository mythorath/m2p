/**
 * Main Leaderboard Component
 */
import { useState, useEffect, useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import leaderboardAPI from '../api/leaderboard';
import { useWebSocket } from '../hooks/useWebSocket';
import type { LeaderboardPeriod, LeaderboardEntry } from '../types/leaderboard';
import './Leaderboard.css';

interface LeaderboardProps {
  walletAddress?: string;
}

export const Leaderboard = ({ walletAddress }: LeaderboardProps) => {
  const [period, setPeriod] = useState<LeaderboardPeriod>('all_time');
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showVerifiedOnly, setShowVerifiedOnly] = useState(false);
  const [highlightWallet, setHighlightWallet] = useState<string | undefined>(walletAddress);

  // WebSocket connection
  const { isConnected, lastMessage } = useWebSocket({
    walletAddress,
    onMessage: (message) => {
      if (message.event === 'leaderboard_updated' && message.data.period === period) {
        // Reload leaderboard data
        loadLeaderboard();
      } else if (message.event === 'rank_changed') {
        // Show notification (can be extended with a toast/notification system)
        console.log('Rank changed:', message.data);
      }
    },
  });

  // Load leaderboard data
  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await leaderboardAPI.getLeaderboard(period, 500, 0);
      setEntries(response.entries);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeaderboard();
  }, [period]);

  // Filter entries based on search and verified filter
  const filteredEntries = useMemo(() => {
    let filtered = entries;

    if (showVerifiedOnly) {
      filtered = filtered.filter((entry) => entry.is_verified);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (entry) =>
          entry.display_name?.toLowerCase().includes(term) ||
          entry.wallet_address.toLowerCase().includes(term)
      );
    }

    return filtered;
  }, [entries, searchTerm, showVerifiedOnly]);

  // Get rank change indicator
  const getRankChangeIndicator = (entry: LeaderboardEntry) => {
    if (!entry.previous_rank) return <span className="rank-change new">NEW</span>;

    const change = entry.previous_rank - entry.rank;
    if (change > 0) {
      return <span className="rank-change up">↑ {change}</span>;
    } else if (change < 0) {
      return <span className="rank-change down">↓ {Math.abs(change)}</span>;
    }
    return <span className="rank-change same">−</span>;
  };

  // Render leaderboard row
  const renderRow = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const entry = filteredEntries[index];
    const isHighlighted = entry.wallet_address === highlightWallet;

    return (
      <div
        style={style}
        className={`leaderboard-row ${isHighlighted ? 'highlighted' : ''} ${
          entry.rank <= 3 ? `rank-${entry.rank}` : ''
        }`}
      >
        <div className="rank-cell">
          <span className="rank-number">#{entry.rank}</span>
          {getRankChangeIndicator(entry)}
        </div>
        <div className="player-cell">
          <span className="display-name">
            {entry.display_name || 'Anonymous'}
            {entry.is_verified && <span className="verified-badge">✓</span>}
          </span>
          <span className="wallet-address">{entry.wallet_truncated}</span>
        </div>
        <div className="stats-cell">
          <div className="stat">
            <span className="stat-label">ADVC:</span>
            <span className="stat-value">{entry.total_mined_advc.toFixed(2)}</span>
          </div>
          <div className="stat">
            <span className="stat-label">AP:</span>
            <span className="stat-value">{entry.total_ap.toLocaleString()}</span>
          </div>
          {period === 'efficiency' && (
            <div className="stat">
              <span className="stat-label">Efficiency:</span>
              <span className="stat-value">{entry.period_score.toFixed(4)}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h1>Leaderboard</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Live' : 'Offline'}
        </div>
      </div>

      {/* Period Tabs */}
      <div className="period-tabs">
        <button
          className={`tab ${period === 'all_time' ? 'active' : ''}`}
          onClick={() => setPeriod('all_time')}
        >
          All Time
        </button>
        <button
          className={`tab ${period === 'this_week' ? 'active' : ''}`}
          onClick={() => setPeriod('this_week')}
        >
          This Week
        </button>
        <button
          className={`tab ${period === 'today' ? 'active' : ''}`}
          onClick={() => setPeriod('today')}
        >
          Today
        </button>
        <button
          className={`tab ${period === 'efficiency' ? 'active' : ''}`}
          onClick={() => setPeriod('efficiency')}
        >
          Efficiency
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search by name or wallet..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={showVerifiedOnly}
            onChange={(e) => setShowVerifiedOnly(e.target.checked)}
          />
          Verified Only
        </label>
      </div>

      {/* Leaderboard List */}
      <div className="leaderboard-list">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : filteredEntries.length === 0 ? (
          <div className="empty">No entries found</div>
        ) : (
          <AutoSizer>
            {({ height, width }) => (
              <List
                height={height}
                itemCount={filteredEntries.length}
                itemSize={80}
                width={width}
              >
                {renderRow}
              </List>
            )}
          </AutoSizer>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
