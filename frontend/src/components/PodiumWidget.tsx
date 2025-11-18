/**
 * Top 3 Podium Display Widget
 */
import { useEffect, useState } from 'react';
import leaderboardAPI from '../api/leaderboard';
import type { LeaderboardPeriod, LeaderboardEntry } from '../types/leaderboard';
import './PodiumWidget.css';

interface PodiumWidgetProps {
  period?: LeaderboardPeriod;
}

export const PodiumWidget = ({ period = 'all_time' }: PodiumWidgetProps) => {
  const [topThree, setTopThree] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTopThree();
  }, [period]);

  const loadTopThree = async () => {
    setLoading(true);
    try {
      const response = await leaderboardAPI.getLeaderboard(period, 3, 0);
      setTopThree(response.entries);
    } catch (error) {
      console.error('Failed to load top 3:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="podium-widget loading">Loading...</div>;
  }

  const [first, second, third] = topThree;

  return (
    <div className="podium-widget">
      <h2 className="podium-title">Top 3</h2>
      <div className="podium-container">
        {/* Second Place */}
        {second && (
          <div className="podium-position second">
            <div className="podium-rank">2</div>
            <div className="podium-player">
              <div className="player-name">{second.display_name || 'Anonymous'}</div>
              <div className="player-score">{second.total_mined_advc.toFixed(2)} ADVC</div>
            </div>
            <div className="podium-stand silver">
              <div className="stand-height"></div>
            </div>
          </div>
        )}

        {/* First Place */}
        {first && (
          <div className="podium-position first">
            <div className="crown">👑</div>
            <div className="podium-rank">1</div>
            <div className="podium-player">
              <div className="player-name">{first.display_name || 'Anonymous'}</div>
              <div className="player-score">{first.total_mined_advc.toFixed(2)} ADVC</div>
            </div>
            <div className="podium-stand gold">
              <div className="stand-height"></div>
            </div>
          </div>
        )}

        {/* Third Place */}
        {third && (
          <div className="podium-position third">
            <div className="podium-rank">3</div>
            <div className="podium-player">
              <div className="player-name">{third.display_name || 'Anonymous'}</div>
              <div className="player-score">{third.total_mined_advc.toFixed(2)} ADVC</div>
            </div>
            <div className="podium-stand bronze">
              <div className="stand-height"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PodiumWidget;
