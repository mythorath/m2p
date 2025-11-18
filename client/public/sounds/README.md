# Sound Effects Directory

This directory contains sound effects for the mining game.

## Required Sound Files

To enable audio in the game, add the following sound files:

### Sound Effects (SFX)
- `coin.mp3` - Played when collecting coins/rewards
- `mining.mp3` - Background mining loop sound
- `achievement.mp3` - Played when unlocking achievements
- `click.mp3` - UI click sound
- `error.mp3` - Error notification sound
- `notification.mp3` - General notification sound

## Sound File Requirements

- **Format**: MP3 (recommended) or OGG
- **Duration**:
  - SFX: 0.5-2 seconds
  - Background music: 30-120 seconds (loopable)
- **Quality**: 128kbps or higher
- **Volume**: Normalized to -3dB to prevent clipping

## Free Sound Resources

You can find free sound effects at:
- [Freesound.org](https://freesound.org/)
- [OpenGameArt.org](https://opengameart.org/)
- [Zapsplat.com](https://www.zapsplat.com/)
- [Mixkit.co](https://mixkit.co/free-sound-effects/)

## License

Ensure all sound files are properly licensed for your use case. Always attribute the original creators if required by the license.

## Adding New Sounds

1. Place the sound file in this directory
2. Update `AudioManager.js` to include the new sound in the `preloadSounds()` function
3. Use `audioManager.play('soundName')` to play the sound in your components

Example:
```javascript
import audioManager from '../utils/AudioManager';

// Play a sound
audioManager.play('coin');

// Play with options
audioManager.play('mining', { loop: true, volume: 0.5 });
```
