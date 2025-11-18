/**
 * Rank Up Progress Bar Widget
 */
import { useEffect, useState } from 'react';
import leaderboardAPI from '../api/leaderboard';
import type { LeaderboardPeriod } from '../types/leaderboard';
import './RankProgressBar.css';

interface RankProgressBarProps {
  walletAddress: string;
  period?: LeaderboardPeriod;
}

export const RankProgressBar = ({ walletAddress, period = 'all_time' }: RankProgressBarProps) => {
  const [currentScore, setCurrentScore] = useState<number>(0);
  const [nextRankScore, setNextRankScore] = useState<number>(0);
  const [currentRank, setCurrentRank] = useState<number>(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProgress();
  }, [walletAddress, period]);

  const loadProgress = async () => {
    setLoading(true);
    try {
      const response = await leaderboardAPI.getPlayerRank(period, walletAddress, 1);
      setCurrentRank(response.player_rank);
      setCurrentScore(response.period_score);

      // Find next rank score from nearby rankings
      const nextRank = response.nearby_rankings.find((r) => r.rank === response.player_rank - 1);
      if (nextRank) {
        setNextRankScore(nextRank.period_score);
      }
    } catch (error) {
      console.error('Failed to load progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgress = () => {
    if (!nextRankScore || nextRankScore === 0) return 0;
    return Math.min((currentScore / nextRankScore) * 100, 100);
  };

  const getScoreNeeded = () => {
    return Math.max(nextRankScore - currentScore, 0);
  };

  if (loading) {
    return <div className="rank-progress loading">Loading...</div>;
  }

  if (currentRank === 1) {
    return (
      <div className="rank-progress">
        <div className="progress-header">
          <span className="progress-title">Rank Progress</span>
        </div>
        <div className="rank-one-message">🏆 You're #1! Keep it up!</div>
      </div>
    );
  }

  const progress = getProgress();
  const scoreNeeded = getScoreNeeded();

  return (
    <div className="rank-progress">
      <div className="progress-header">
        <span className="progress-title">Rank Up Progress</span>
        <span className="progress-subtitle">
          To Rank #{currentRank - 1}
        </span>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          >
            <div className="progress-shine"></div>
          </div>
        </div>
        <div className="progress-text">{progress.toFixed(1)}%</div>
      </div>

      <div className="progress-stats">
        <div className="stat">
          <span className="stat-label">Current Score</span>
          <span className="stat-value">{currentScore.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Score Needed</span>
          <span className="stat-value highlight">{scoreNeeded.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

export default RankProgressBar;
