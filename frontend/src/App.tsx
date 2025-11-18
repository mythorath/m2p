/**
 * Main App Component
 */
import { useState } from 'react';
import { Leaderboard } from './components/Leaderboard';
import { PodiumWidget } from './components/PodiumWidget';
import { RankBadge } from './components/RankBadge';
import { RankProgressBar } from './components/RankProgressBar';
import type { LeaderboardPeriod } from './types/leaderboard';
import './App.css';

function App() {
  const [walletAddress, setWalletAddress] = useState<string>('');
  const [period, setPeriod] = useState<LeaderboardPeriod>('all_time');
  const [showWidgets, setShowWidgets] = useState(false);

  return (
    <div className="app">
      <div className="app-header">
        <div className="header-content">
          <h1 className="app-title">M2P Leaderboard</h1>
          <div className="wallet-input-container">
            <input
              type="text"
              placeholder="Enter your wallet address..."
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              className="wallet-input"
            />
            {walletAddress && (
              <button
                onClick={() => setShowWidgets(!showWidgets)}
                className="toggle-widgets-btn"
              >
                {showWidgets ? 'Hide' : 'Show'} Widgets
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="app-content">
        {showWidgets && walletAddress && (
          <div className="widgets-sidebar">
            <PodiumWidget period={period} />
            <RankBadge walletAddress={walletAddress} period={period} />
            <RankProgressBar walletAddress={walletAddress} period={period} />
          </div>
        )}

        <div className="main-content">
          <Leaderboard walletAddress={walletAddress || undefined} />
        </div>
      </div>
    </div>
  );
}

export default App;
