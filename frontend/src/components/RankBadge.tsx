/**
 * Player Rank Badge Widget
 */
import { useEffect, useState } from 'react';
import leaderboardAPI from '../api/leaderboard';
import type { LeaderboardPeriod } from '../types/leaderboard';
import './RankBadge.css';

interface RankBadgeProps {
  walletAddress: string;
  period?: LeaderboardPeriod;
}

export const RankBadge = ({ walletAddress, period = 'all_time' }: RankBadgeProps) => {
  const [rank, setRank] = useState<number | null>(null);
  const [previousRank, setPreviousRank] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRank();
  }, [walletAddress, period]);

  const loadRank = async () => {
    setLoading(true);
    try {
      const response = await leaderboardAPI.getPlayerRank(period, walletAddress);
      setRank(response.player_rank);
      setPreviousRank(response.previous_rank);
    } catch (error) {
      console.error('Failed to load rank:', error);
      setRank(null);
    } finally {
      setLoading(false);
    }
  };

  const getRankChange = () => {
    if (!previousRank || !rank) return null;
    const change = previousRank - rank;
    if (change > 0) return { direction: 'up', value: change };
    if (change < 0) return { direction: 'down', value: Math.abs(change) };
    return null;
  };

  const rankChange = getRankChange();

  if (loading) {
    return <div className="rank-badge loading">Loading...</div>;
  }

  if (!rank) {
    return <div className="rank-badge unranked">Not Ranked</div>;
  }

  return (
    <div className={`rank-badge ${rank <= 3 ? `top-${rank}` : ''}`}>
      <div className="rank-label">Your Rank</div>
      <div className="rank-value">#{rank}</div>
      {rankChange && (
        <div className={`rank-change ${rankChange.direction}`}>
          {rankChange.direction === 'up' ? '↑' : '↓'} {rankChange.value}
        </div>
      )}
    </div>
  );
};

export default RankBadge;
