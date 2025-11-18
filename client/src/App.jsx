/**
 * Main App Component for M2P (Mine to Play)
 * Demonstrates achievement popup integration with WebSocket
 */
import React, { useState } from 'react';
import AchievementUnlockPopup from './components/AchievementUnlockPopup';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  const [playerId, setPlayerId] = useState(1); // Replace with actual auth
  const {
    isConnected,
    achievementNotification,
    clearAchievementNotification,
  } = useWebSocket(playerId);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1>🎮 M2P - Mine to Play</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="container">
          <h2>Achievement System Demo</h2>
          <p>When you unlock an achievement, a popup will appear!</p>

          {/* Demo section */}
          <div className="demo-section">
            <h3>WebSocket Status</h3>
            <p>Player ID: {playerId}</p>
            <p>Connection: {isConnected ? '✅ Connected' : '❌ Disconnected'}</p>
          </div>

          {/* Instructions */}
          <div className="info-section">
            <h3>How to Test</h3>
            <ol>
              <li>Start the backend server: <code>python server/app.py</code></li>
              <li>Seed achievements: <code>python server/seed_achievements.py</code></li>
              <li>Send a mining reward via API to trigger achievement checks</li>
              <li>Watch for the achievement unlock popup!</li>
            </ol>
          </div>

          {/* API Example */}
          <div className="code-section">
            <h3>API Example - Process Mining Reward</h3>
            <pre>
{`curl -X POST http://localhost:5000/api/mining/reward \\
  -H "Content-Type: application/json" \\
  -d '{
    "player_id": 1,
    "amount": 0.001,
    "pool_id": "pool_1",
    "pool_name": "MainPool"
  }'`}
            </pre>
          </div>
        </div>
      </main>

      {/* Achievement Unlock Popup */}
      {achievementNotification && (
        <AchievementUnlockPopup
          achievement={achievementNotification}
          onClose={clearAchievementNotification}
        />
      )}
    </div>
  );
}

export default App;
