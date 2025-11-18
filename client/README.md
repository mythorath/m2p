# Mining Game - Client

A feature-rich mining game client with engaging visualizations and animations built with React.

## Features

### 🎮 Game Visualizations
- **MiningScene Component**: Interactive mining scene with:
  - Canvas-based rendering
  - Parallax background layers
  - Animated ore veins with glow effects
  - Dynamic efficiency meter
  - Click-to-mine interaction

### 🎨 Animations
- **MinerSprite**: Animated miner character with multiple states:
  - Idle (breathing animation)
  - Mining (pickaxe swing)
  - Celebrating (victory dance)
  - Supports both sprite sheets and CSS-only fallback

- **ParticleEffect**: Reusable particle system for:
  - Coins (on rewards)
  - Sparkles (mining effects)
  - Explosions (achievements)
  - Dust (ambient effects)

- **APCounter**: Animated number counter with:
  - Smooth increment animations
  - Glow effects on value change
  - Large number formatting (K, M, B)

### 📊 UI Components
- **ProgressBar**: Animated progress bars with:
  - Multiple variants (achievement, mining, health, energy, experience)
  - Gradient backgrounds
  - Shine effects
  - Customizable colors

- **LoadingStates**: Comprehensive loading components:
  - Spinner
  - Skeleton loaders
  - Dots loader
  - Pulse loader
  - Progress circle
  - Loading overlay
  - Mining-themed loader

### 🔊 Audio System
- **AudioManager**: Complete audio management with:
  - Volume control (master, music, SFX)
  - Mute toggle
  - Sound pooling for performance
  - Background music looping
  - Browser audio policy compliance
  - Settings persistence

- **AudioControls**: UI component for audio settings

### 🔔 Notifications
- **Notification System** using react-toastify:
  - Success, info, warning, error types
  - Achievement notifications
  - Reward notifications
  - Mining notifications
  - Auto-dismiss
  - Stackable notifications

### ⚡ Performance Optimizations
- **usePerformance Hook**: Device capability detection
  - Mobile detection
  - Reduced motion support
  - FPS monitoring
  - Automatic quality adjustment

- **useAnimations Hook**: Dynamic animation settings
  - Conditional particle effects
  - Adaptive particle counts
  - Performance-based quality

- **CanvasOptimizer**: Canvas rendering optimizations
  - High DPI support
  - Offscreen canvas
  - Efficient rendering

- **ObjectPool**: Object pooling for particle systems

## Installation

```bash
cd client
npm install
```

## Development

```bash
npm start
```

Runs the app in development mode at [http://localhost:3000](http://localhost:3000)

## Build

```bash
npm run build
```

Builds the app for production to the `build` folder.

## Project Structure

```
client/
├── public/
│   ├── sounds/          # Sound effect files
│   └── index.html
├── src/
│   ├── animations/      # Sprite sheets and animation assets
│   ├── components/      # React components
│   │   ├── MiningScene.js        # Main game scene
│   │   ├── MinerSprite.js        # Animated miner
│   │   ├── ParticleEffect.js     # Particle system
│   │   ├── APCounter.js          # Animated counter
│   │   ├── ProgressBar.js        # Progress bars
│   │   ├── LoadingStates.js      # Loading components
│   │   └── AudioControls.js      # Audio UI
│   ├── hooks/           # Custom React hooks
│   │   └── usePerformance.js     # Performance hooks
│   ├── utils/           # Utility functions
│   │   ├── AudioManager.js       # Audio system
│   │   ├── notifications.js      # Notification helpers
│   │   └── performanceOptimizer.js # Performance utils
│   ├── App.js           # Main app component
│   ├── App.css          # App styles
│   ├── index.js         # Entry point
│   └── index.css        # Global styles
└── package.json
```

## Component Usage

### MiningScene

```javascript
import MiningScene from './components/MiningScene';

<MiningScene
  miningRate={5.5}
  pendingRewards={100}
  onMine={() => console.log('Mined!')}
  isActive={true}
  efficiency={0.8}
  achievements={['first_mine']}
  width={800}
  height={600}
/>
```

### APCounter

```javascript
import APCounter from './components/APCounter';

<APCounter
  value={1234}
  label="Action Points"
  glowColor="#FFD700"
  fontSize="2rem"
  formatNumber={true}
/>
```

### ProgressBar

```javascript
import ProgressBar from './components/ProgressBar';

<ProgressBar
  value={75}
  max={100}
  variant="achievement"
  label="Achievement Progress"
  showPercentage={true}
  height="24px"
/>
```

### ParticleEffect

```javascript
import ParticleEffect from './components/ParticleEffect';

<ParticleEffect
  type="coin"
  x={100}
  y={200}
  count={20}
  duration={1000}
  onComplete={() => console.log('Done!')}
/>
```

### Audio System

```javascript
import audioManager from './utils/AudioManager';
import { notify } from './utils/notifications';

// Initialize (after user interaction)
audioManager.init();

// Play sound
audioManager.play('coin');
audioManager.play('mining', { loop: true, volume: 0.5 });

// Music
audioManager.playMusic('background', { fadeIn: true });
audioManager.stopMusic();

// Notifications
notify.success('Mining started!');
notify.achievement('Master Miner', 'Reached level 10');
notify.reward(100, 'AP');
```

## Adding Assets

### Sound Effects

1. Place sound files in `public/sounds/`
2. Update `AudioManager.js` to preload them
3. Supported formats: MP3, OGG

See `public/sounds/README.md` for details.

### Sprite Sheets

1. Create a sprite sheet following the format in `src/animations/README.md`
2. Save as `miner-sprites.png` in `src/animations/`
3. Set `useSpriteSheet={true}` in MinerSprite component

## Performance

The app automatically adjusts quality based on:
- Device capabilities (mobile/desktop)
- User preferences (reduced motion)
- Current FPS
- Battery status

Quality levels:
- **High**: All effects enabled, 60 FPS, 30 particles
- **Medium**: Reduced effects, 30 FPS, 15 particles
- **Low**: Minimal effects, 20 FPS, 5 particles

## Accessibility

- Reduced motion support
- High contrast mode
- Keyboard navigation
- ARIA labels
- Focus indicators

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT

## Credits

Built with:
- React 18
- react-spring (animations)
- framer-motion (animations)
- react-toastify (notifications)
