/**
 * Audio Manager for game sounds
 * Features:
 * - Volume control
 * - Mute toggle
 * - Browser audio policy compliance
 * - Multiple sound channels
 * - Sound pooling for performance
 * - Background music loop
 */

class AudioManager {
  constructor() {
    this.sounds = {};
    this.volume = 0.7;
    this.muted = false;
    this.musicVolume = 0.5;
    this.sfxVolume = 0.7;
    this.initialized = false;
    this.context = null;
    this.currentMusic = null;

    // Sound pools for frequently used sounds
    this.soundPools = {};
    this.poolSize = 5;

    // Load settings from localStorage
    this.loadSettings();
  }

  /**
   * Initialize audio context (must be called after user interaction)
   */
  async init() {
    if (this.initialized) return;

    try {
      // Create audio context
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.context = new AudioContext();

      // Preload sounds
      await this.preloadSounds();

      this.initialized = true;
      console.log('AudioManager initialized');
    } catch (error) {
      console.error('Failed to initialize AudioManager:', error);
    }
  }

  /**
   * Preload all game sounds
   */
  async preloadSounds() {
    const soundFiles = {
      coin: '/sounds/coin.mp3',
      mining: '/sounds/mining.mp3',
      achievement: '/sounds/achievement.mp3',
      click: '/sounds/click.mp3',
      error: '/sounds/error.mp3',
      notification: '/sounds/notification.mp3'
    };

    const loadPromises = Object.entries(soundFiles).map(async ([name, path]) => {
      try {
        await this.loadSound(name, path);
      } catch (error) {
        console.warn(`Failed to load sound: ${name}`, error);
      }
    });

    await Promise.all(loadPromises);
  }

  /**
   * Load a sound file
   */
  async loadSound(name, path) {
    return new Promise((resolve, reject) => {
      const audio = new Audio(path);
      audio.preload = 'auto';

      audio.addEventListener('canplaythrough', () => {
        this.sounds[name] = audio;
        resolve();
      });

      audio.addEventListener('error', (e) => {
        reject(e);
      });

      // Create sound pool for frequently used sounds
      if (['coin', 'click'].includes(name)) {
        this.soundPools[name] = [];
        for (let i = 0; i < this.poolSize; i++) {
          const pooledAudio = new Audio(path);
          pooledAudio.preload = 'auto';
          this.soundPools[name].push(pooledAudio);
        }
      }
    });
  }

  /**
   * Play a sound effect
   */
  play(soundName, options = {}) {
    if (!this.initialized || this.muted) return;

    const {
      volume = this.sfxVolume,
      loop = false,
      playbackRate = 1.0
    } = options;

    // Use sound pool if available
    if (this.soundPools[soundName]) {
      const pooledSound = this.soundPools[soundName].find(
        (sound) => sound.paused || sound.ended
      );

      if (pooledSound) {
        pooledSound.volume = volume * this.volume;
        pooledSound.loop = loop;
        pooledSound.playbackRate = playbackRate;
        pooledSound.currentTime = 0;
        pooledSound.play().catch((e) => console.warn('Audio play failed:', e));
        return pooledSound;
      }
    }

    // Fallback to regular sound
    const sound = this.sounds[soundName];
    if (!sound) {
      console.warn(`Sound not found: ${soundName}`);
      return;
    }

    // Clone the audio for overlapping sounds
    const soundClone = sound.cloneNode();
    soundClone.volume = volume * this.volume;
    soundClone.loop = loop;
    soundClone.playbackRate = playbackRate;
    soundClone.play().catch((e) => console.warn('Audio play failed:', e));

    return soundClone;
  }

  /**
   * Play background music
   */
  playMusic(musicName, options = {}) {
    if (!this.initialized) return;

    const { volume = this.musicVolume, fadeIn = true } = options;

    // Stop current music
    if (this.currentMusic) {
      this.stopMusic();
    }

    const music = this.sounds[musicName];
    if (!music) {
      console.warn(`Music not found: ${musicName}`);
      return;
    }

    this.currentMusic = music.cloneNode();
    this.currentMusic.loop = true;

    if (fadeIn) {
      this.currentMusic.volume = 0;
      this.currentMusic.play().catch((e) => console.warn('Music play failed:', e));
      this.fadeTo(this.currentMusic, volume * this.volume, 2000);
    } else {
      this.currentMusic.volume = volume * this.volume;
      this.currentMusic.play().catch((e) => console.warn('Music play failed:', e));
    }

    return this.currentMusic;
  }

  /**
   * Stop background music
   */
  stopMusic(fadeOut = true) {
    if (!this.currentMusic) return;

    if (fadeOut) {
      this.fadeTo(this.currentMusic, 0, 1000, () => {
        this.currentMusic.pause();
        this.currentMusic = null;
      });
    } else {
      this.currentMusic.pause();
      this.currentMusic = null;
    }
  }

  /**
   * Fade audio volume
   */
  fadeTo(audio, targetVolume, duration, callback) {
    const startVolume = audio.volume;
    const volumeChange = targetVolume - startVolume;
    const steps = 20;
    const stepTime = duration / steps;
    let currentStep = 0;

    const fadeInterval = setInterval(() => {
      currentStep++;
      audio.volume = startVolume + (volumeChange * currentStep) / steps;

      if (currentStep >= steps) {
        clearInterval(fadeInterval);
        audio.volume = targetVolume;
        if (callback) callback();
      }
    }, stepTime);
  }

  /**
   * Set master volume
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    this.saveSettings();

    // Update current music volume
    if (this.currentMusic) {
      this.currentMusic.volume = this.musicVolume * this.volume;
    }
  }

  /**
   * Set music volume
   */
  setMusicVolume(volume) {
    this.musicVolume = Math.max(0, Math.min(1, volume));
    this.saveSettings();

    if (this.currentMusic) {
      this.currentMusic.volume = this.musicVolume * this.volume;
    }
  }

  /**
   * Set SFX volume
   */
  setSFXVolume(volume) {
    this.sfxVolume = Math.max(0, Math.min(1, volume));
    this.saveSettings();
  }

  /**
   * Toggle mute
   */
  toggleMute() {
    this.muted = !this.muted;
    this.saveSettings();

    if (this.currentMusic) {
      this.currentMusic.volume = this.muted ? 0 : this.musicVolume * this.volume;
    }

    return this.muted;
  }

  /**
   * Save settings to localStorage
   */
  saveSettings() {
    const settings = {
      volume: this.volume,
      musicVolume: this.musicVolume,
      sfxVolume: this.sfxVolume,
      muted: this.muted
    };
    localStorage.setItem('audioSettings', JSON.stringify(settings));
  }

  /**
   * Load settings from localStorage
   */
  loadSettings() {
    const savedSettings = localStorage.getItem('audioSettings');
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        this.volume = settings.volume ?? 0.7;
        this.musicVolume = settings.musicVolume ?? 0.5;
        this.sfxVolume = settings.sfxVolume ?? 0.7;
        this.muted = settings.muted ?? false;
      } catch (error) {
        console.error('Failed to load audio settings:', error);
      }
    }
  }

  /**
   * Get current settings
   */
  getSettings() {
    return {
      volume: this.volume,
      musicVolume: this.musicVolume,
      sfxVolume: this.sfxVolume,
      muted: this.muted,
      initialized: this.initialized
    };
  }

  /**
   * Stop all sounds
   */
  stopAll() {
    this.stopMusic(false);

    // Stop pooled sounds
    Object.values(this.soundPools).forEach((pool) => {
      pool.forEach((sound) => {
        sound.pause();
        sound.currentTime = 0;
      });
    });
  }
}

// Create singleton instance
const audioManager = new AudioManager();

export default audioManager;
