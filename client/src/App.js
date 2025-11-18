import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import MiningScene from './components/MiningScene';
import APCounter from './components/APCounter';
import ProgressBar from './components/ProgressBar';
import AudioControls from './components/AudioControls';
import { LoadingOverlay, MiningLoader, SkeletonCard } from './components/LoadingStates';
import { notify } from './utils/notifications';
import { usePerformance, useAnimations } from './hooks/usePerformance';
import audioManager from './utils/AudioManager';
import './App.css';
import './utils/notifications.css';

/**
 * Main Application Component
 * Demonstrates all game visualization and animation components
 */

function App() {
  const [ap, setAp] = useState(1000);
  const [miningRate, setMiningRate] = useState(0);
  const [isMining, setIsMining] = useState(false);
  const [pendingRewards, setPendingRewards] = useState(0);
  const [efficiency, setEfficiency] = useState(0.8);
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [xp, setXp] = useState(250);
  const [maxXp] = useState(500);

  const performance = usePerformance();
  const animations = useAnimations();

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  // Mining loop
  useEffect(() => {
    if (!isMining) return;

    const interval = setInterval(() => {
      const reward = Math.floor(Math.random() * 10) + 5;
      setAp(prev => prev + reward);
      setPendingRewards(prev => prev + reward);
      setMiningRate(reward / 2);
      setXp(prev => Math.min(prev + 5, maxXp));

      // Play mining sound
      if (Math.random() > 0.7) {
        audioManager.play('mining', { volume: 0.3 });
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isMining, maxXp]);

  // Clear pending rewards
  useEffect(() => {
    if (pendingRewards === 0) return;

    const timer = setTimeout(() => {
      setPendingRewards(0);
      notify.reward(pendingRewards, 'AP');
      audioManager.play('coin');
    }, 5000);

    return () => clearTimeout(timer);
  }, [pendingRewards]);

  // Check for achievements
  useEffect(() => {
    if (ap >= 2000 && !achievements.includes('first_thousand')) {
      setAchievements(prev => [...prev, 'first_thousand']);
      notify.achievement(
        'Wealthy Miner!',
        'Accumulated 2000 AP',
        { autoClose: 5000 }
      );
      audioManager.play('achievement');
    }
  }, [ap, achievements]);

  // Handle manual mining
  const handleMine = () => {
    const reward = Math.floor(Math.random() * 20) + 10;
    setAp(prev => prev + reward);
    setPendingRewards(prev => prev + reward);
    notify.mining(`+${reward} AP`, { autoClose: 1500 });
    audioManager.play('click');
  };

  // Toggle auto mining
  const toggleMining = () => {
    setIsMining(!isMining);
    if (!isMining) {
      notify.success('Auto-mining started!');
      audioManager.play('click');
    } else {
      notify.info('Auto-mining stopped');
      setMiningRate(0);
      audioManager.play('click');
    }
  };

  // Test notifications
  const testNotifications = () => {
    notify.success('Success notification!');
    setTimeout(() => notify.warning('Warning notification!'), 500);
    setTimeout(() => notify.error('Error notification!'), 1000);
    setTimeout(() => notify.info('Info notification!'), 1500);
  };

  if (loading) {
    return (
      <div className="app">
        <LoadingOverlay loading={true} type="pulse" message="Loading Mining Game...">
          <div style={{ padding: '40px' }}>
            <SkeletonCard />
          </div>
        </LoadingOverlay>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>⛏️ Mining Game Demo</h1>
        <div className="performance-badge">
          Quality: {performance.quality.toUpperCase()}
          {performance.fps > 0 && ` | ${performance.fps} FPS`}
        </div>
      </header>

      <main className="app-main">
        {/* Stats Panel */}
        <div className="stats-panel">
          <APCounter
            value={ap}
            label="Action Points"
            glowColor="#FFD700"
            fontSize="2.5rem"
          />

          <APCounter
            value={miningRate}
            label="Mining Rate"
            glowColor="#00BFFF"
            fontSize="1.5rem"
            suffix=" AP/s"
            decimals={2}
          />
        </div>

        {/* Mining Scene */}
        <div className="game-container">
          <MiningScene
            miningRate={miningRate}
            pendingRewards={pendingRewards}
            onMine={handleMine}
            isActive={isMining}
            efficiency={efficiency}
            achievements={achievements}
            width={800}
            height={600}
          />
        </div>

        {/* Progress Bars */}
        <div className="progress-section">
          <ProgressBar
            value={xp}
            max={maxXp}
            variant="experience"
            label="Experience"
            showPercentage={false}
            height="30px"
          />

          <ProgressBar
            value={efficiency * 100}
            max={100}
            variant="mining"
            label="Mining Efficiency"
            showPercentage={true}
            height="24px"
          />

          <ProgressBar
            value={75}
            max={100}
            variant="achievement"
            label="Achievement Progress"
            showPercentage={true}
            height="24px"
          />
        </div>

        {/* Controls */}
        <div className="controls-panel">
          <button
            className={`btn btn-primary ${isMining ? 'active' : ''}`}
            onClick={toggleMining}
          >
            {isMining ? '⏸️ Stop Mining' : '▶️ Start Mining'}
          </button>

          <button
            className="btn btn-secondary"
            onClick={handleMine}
          >
            ⛏️ Mine Once
          </button>

          <button
            className="btn btn-info"
            onClick={testNotifications}
          >
            🔔 Test Notifications
          </button>

          <button
            className="btn btn-warning"
            onClick={() => {
              setEfficiency(Math.random());
              notify.info(`Efficiency changed to ${(efficiency * 100).toFixed(0)}%`);
            }}
          >
            🔄 Random Efficiency
          </button>
        </div>

        {/* Animation Info */}
        <div className="info-panel">
          <h3>Animation Settings</h3>
          <ul>
            <li>Particles Enabled: {animations.enableParticles ? '✅' : '❌'}</li>
            <li>Particle Count: {animations.particleCount}</li>
            <li>Glow Effects: {animations.enableGlow ? '✅' : '❌'}</li>
            <li>Shadows: {animations.enableShadows ? '✅' : '❌'}</li>
            <li>Target FPS: {animations.fps}</li>
            <li>Mobile: {performance.isMobile ? '✅' : '❌'}</li>
            <li>Reduced Motion: {performance.reducedMotion ? '✅' : '❌'}</li>
          </ul>
        </div>
      </main>

      {/* Audio Controls */}
      <AudioControls />

      {/* Toast Notifications */}
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </div>
  );
}

export default App;
