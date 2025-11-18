/**
 * Achievement Unlock Popup Component
 * Displays an animated popup when a player unlocks an achievement
 */
import React, { useEffect, useState } from 'react';
import './AchievementUnlockPopup.css';

const AchievementUnlockPopup = ({ achievement, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setIsVisible(true), 100);

    // Play sound effect
    playUnlockSound();

    // Auto-dismiss after 5 seconds
    const timer = setTimeout(() => {
      handleClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  const playUnlockSound = () => {
    try {
      // Create achievement unlock sound
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // Achievement fanfare notes
      const notes = [
        { freq: 523.25, time: 0, duration: 0.15 },     // C5
        { freq: 659.25, time: 0.15, duration: 0.15 },  // E5
        { freq: 783.99, time: 0.3, duration: 0.3 },    // G5
      ];

      oscillator.type = 'sine';
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);

      notes.forEach(note => {
        oscillator.frequency.setValueAtTime(note.freq, audioContext.currentTime + note.time);
      });

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.6);

      // Cleanup
      setTimeout(() => {
        audioContext.close();
      }, 1000);
    } catch (error) {
      console.error('Error playing sound:', error);
    }
  };

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      if (onClose) onClose();
    }, 300);
  };

  if (!achievement) return null;

  return (
    <div className={`achievement-overlay ${isVisible ? 'visible' : ''} ${isExiting ? 'exiting' : ''}`}>
      <div className={`achievement-popup ${isVisible ? 'show' : ''} ${isExiting ? 'hide' : ''}`}>
        {/* Close button */}
        <button className="achievement-close" onClick={handleClose}>
          ×
        </button>

        {/* Header */}
        <div className="achievement-header">
          <div className="achievement-shine"></div>
          <h2 className="achievement-title">Achievement Unlocked!</h2>
        </div>

        {/* Icon */}
        <div className="achievement-icon-wrapper">
          <div className="achievement-icon-glow"></div>
          <div className="achievement-icon">{achievement.icon}</div>
          <div className="achievement-particles">
            {[...Array(12)].map((_, i) => (
              <div key={i} className="particle" style={{
                '--angle': `${i * 30}deg`,
                '--delay': `${i * 0.1}s`
              }}></div>
            ))}
          </div>
        </div>

        {/* Achievement info */}
        <div className="achievement-info">
          <h3 className="achievement-name">{achievement.name}</h3>
          <p className="achievement-description">{achievement.description}</p>

          {/* AP Reward */}
          <div className="achievement-reward">
            <div className="ap-badge">
              <span className="ap-icon">⭐</span>
              <span className="ap-amount">+{achievement.ap_reward} AP</span>
            </div>
          </div>

          {/* Category badge */}
          {achievement.category && (
            <div className="achievement-category">
              <span className="category-badge">{achievement.category}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="achievement-footer">
          <button className="achievement-dismiss" onClick={handleClose}>
            Awesome!
          </button>
        </div>
      </div>
    </div>
  );
};

export default AchievementUnlockPopup;
