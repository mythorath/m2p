import React, { useState, useEffect } from 'react';
import audioManager from '../utils/AudioManager';
import './AudioControls.css';

/**
 * Audio control panel component
 * Provides UI for volume control and mute toggle
 */

const AudioControls = ({ className = '' }) => {
  const [settings, setSettings] = useState(audioManager.getSettings());
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    // Initialize audio manager on first user interaction
    const initAudio = () => {
      if (!audioManager.initialized) {
        audioManager.init();
        setSettings(audioManager.getSettings());
      }
    };

    document.addEventListener('click', initAudio, { once: true });
    return () => document.removeEventListener('click', initAudio);
  }, []);

  const handleVolumeChange = (e) => {
    const volume = parseFloat(e.target.value);
    audioManager.setVolume(volume);
    setSettings(audioManager.getSettings());
  };

  const handleMusicVolumeChange = (e) => {
    const volume = parseFloat(e.target.value);
    audioManager.setMusicVolume(volume);
    setSettings(audioManager.getSettings());
  };

  const handleSFXVolumeChange = (e) => {
    const volume = parseFloat(e.target.value);
    audioManager.setSFXVolume(volume);
    setSettings(audioManager.getSettings());
  };

  const handleMuteToggle = () => {
    audioManager.toggleMute();
    setSettings(audioManager.getSettings());
  };

  return (
    <div className={`audio-controls ${className} ${expanded ? 'expanded' : ''}`}>
      <button
        className="audio-toggle-btn"
        onClick={() => setExpanded(!expanded)}
        title={settings.muted ? 'Unmute' : 'Mute'}
      >
        {settings.muted ? '🔇' : settings.volume > 0.5 ? '🔊' : settings.volume > 0 ? '🔉' : '🔈'}
      </button>

      {expanded && (
        <div className="audio-controls-panel">
          <div className="audio-control-group">
            <label className="audio-control-label">
              Master
              <span className="audio-control-value">
                {Math.round(settings.volume * 100)}%
              </span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={settings.volume}
              onChange={handleVolumeChange}
              className="audio-slider"
            />
          </div>

          <div className="audio-control-group">
            <label className="audio-control-label">
              Music
              <span className="audio-control-value">
                {Math.round(settings.musicVolume * 100)}%
              </span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={settings.musicVolume}
              onChange={handleMusicVolumeChange}
              className="audio-slider"
            />
          </div>

          <div className="audio-control-group">
            <label className="audio-control-label">
              SFX
              <span className="audio-control-value">
                {Math.round(settings.sfxVolume * 100)}%
              </span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={settings.sfxVolume}
              onChange={handleSFXVolumeChange}
              className="audio-slider"
            />
          </div>

          <button
            className={`audio-mute-btn ${settings.muted ? 'muted' : ''}`}
            onClick={handleMuteToggle}
          >
            {settings.muted ? 'Unmute' : 'Mute All'}
          </button>
        </div>
      )}
    </div>
  );
};

export default AudioControls;
