# M2P - Mining Game with Visualizations & Animations

A feature-rich mining game with engaging visualizations, animations, and interactive gameplay elements.

## 🎮 Project Overview

This project implements **Agent 6: Game Visualizations & Animations** for a mining game, featuring:

- Canvas-based game scenes with parallax backgrounds
- Animated sprite system with multiple character states
- Advanced particle effects system
- Animated UI components (counters, progress bars)
- Complete audio management system
- Toast notification system
- Performance optimizations for various devices
- Accessibility features

## 📦 Project Structure

```
m2p/
├── client/                 # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── utils/         # Utility functions
│   │   ├── animations/    # Sprite sheets & assets
│   │   └── App.js         # Main application
│   ├── public/
│   │   └── sounds/        # Audio files
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
cd client
npm run build
```

## 🎨 Features

### 1. MiningScene Component
Interactive mining environment with:
- Canvas-based rendering with parallax layers
- Animated ore veins with dynamic glow effects
- Particle effects on mining actions
- Real-time mining rate visualization
- Efficiency meter
- Click-to-mine interaction

### 2. Sprite Animation System
Animated miner character featuring:
- **Idle state**: Breathing animation
- **Mining state**: Pickaxe swing animation
- **Celebrating state**: Victory dance
- Dual mode: Sprite sheet or CSS-only fallback
- 8-bit/pixel art style

### 3. Particle Effect System
Reusable, performance-optimized particle system:
- **Coin particles**: On reward collection
- **Sparkle particles**: Mining effects
- **Explosion particles**: Achievement unlocks
- **Dust particles**: Ambient effects
- Canvas-based rendering with requestAnimationFrame
- Configurable count, duration, and appearance

### 4. Animated Components

#### APCounter
- Smooth number increment animations using react-spring
- Glow effect on value changes
- Large number formatting (K, M, B)
- Customizable colors and sizes

#### ProgressBar
Multiple variants with animated fills:
- Achievement progress
- Mining efficiency
- Experience bars
- Health/energy bars
- Gradient backgrounds with shine effects

### 5. Audio Manager
Complete audio system with:
- Volume controls (master, music, SFX)
- Mute/unmute functionality
- Sound pooling for performance
- Background music with fade in/out
- Browser audio policy compliance
- Settings persistence via localStorage
- UI controls component

### 6. Notification System
Toast notifications using react-toastify:
- Success, info, warning, error types
- Custom achievement notifications
- Reward notifications with animations
- Auto-dismiss and manual close
- Stack multiple notifications
- Top-right positioning

### 7. Loading States
Comprehensive loading components:
- Spinners (multiple styles)
- Skeleton screens with shimmer effects
- Progress circles
- Dots loader
- Pulse loader
- Loading overlays
- Mining-themed loader

### 8. Performance Optimizations

#### Responsive Design
- Mobile/tablet/desktop detection
- Adaptive quality settings
- FPS monitoring and throttling
- Particle count adjustment

#### Accessibility
- Reduced motion support
- High contrast mode
- Keyboard navigation
- ARIA labels
- Focus indicators

#### Performance Features
- Canvas optimization with offscreen rendering
- Object pooling for particles
- RequestAnimationFrame throttling
- Automatic quality adjustment based on device
- Low-end device detection

## 📚 Component Documentation

### MiningScene

```javascript
<MiningScene
  miningRate={5.5}          // Current mining rate (AP/s)
  pendingRewards={100}      // Pending rewards to display
  onMine={() => {}}         // Callback when user clicks to mine
  isActive={true}           // Whether mining is active
  efficiency={0.8}          // Mining efficiency (0-1)
  achievements={[]}         // Array of unlocked achievements
  width={800}               // Scene width
  height={600}              // Scene height
/>
```

### APCounter

```javascript
<APCounter
  value={1234}              // Current value
  label="Action Points"     // Label text
  glowColor="#FFD700"       // Glow effect color
  fontSize="2rem"           // Font size
  formatNumber={true}       // Enable K/M/B formatting
  decimals={0}              // Decimal places
  prefix=""                 // Text before value
  suffix=""                 // Text after value
/>
```

### ProgressBar

```javascript
<ProgressBar
  value={75}                // Current value
  max={100}                 // Maximum value
  variant="achievement"     // Style variant
  label="Progress"          // Label text
  showPercentage={true}     // Show percentage
  height="24px"             // Bar height
  animated={true}           // Enable animations
/>
```

Variants: `default`, `achievement`, `mining`, `health`, `energy`, `experience`

### ParticleEffect

```javascript
<ParticleEffect
  type="coin"               // Particle type
  x={100}                   // X position
  y={200}                   // Y position
  count={20}                // Number of particles
  duration={1000}           // Animation duration (ms)
  onComplete={() => {}}     // Callback when complete
  active={true}             // Trigger animation
  width={300}               // Canvas width
  height={300}              // Canvas height
/>
```

Types: `coin`, `sparkle`, `explosion`, `dust`

### Audio System

```javascript
import audioManager from './utils/AudioManager';

// Initialize (call after user interaction)
await audioManager.init();

// Play sound effect
audioManager.play('coin');
audioManager.play('mining', {
  loop: true,
  volume: 0.5,
  playbackRate: 1.0
});

// Play background music
audioManager.playMusic('background', { fadeIn: true });

// Stop music
audioManager.stopMusic(/* fadeOut */ true);

// Volume controls
audioManager.setVolume(0.7);           // Master volume
audioManager.setMusicVolume(0.5);      // Music volume
audioManager.setSFXVolume(0.8);        // SFX volume
audioManager.toggleMute();              // Toggle mute
```

### Notifications

```javascript
import { notify } from './utils/notifications';

// Basic notifications
notify.success('Success message');
notify.info('Info message');
notify.warning('Warning message');
notify.error('Error message');

// Special notifications
notify.achievement('Title', 'Description');
notify.reward(100, 'AP');
notify.mining('Mining message');

// Promise-based
notify.promise(
  someAsyncOperation(),
  {
    pending: 'Processing...',
    success: 'Success!',
    error: 'Failed!'
  }
);
```

## 🎯 Performance Hooks

### usePerformance

```javascript
import { usePerformance } from './hooks/usePerformance';

const performance = usePerformance();
// Returns: { isMobile, reducedMotion, lowPowerMode, quality, fps }
```

### useAnimations

```javascript
import { useAnimations } from './hooks/usePerformance';

const animations = useAnimations();
// Returns: {
//   enableParticles,
//   enableTransitions,
//   particleCount,
//   enableGlow,
//   enableShadows,
//   fps
// }
```

### useViewport

```javascript
import { useViewport } from './hooks/usePerformance';

const viewport = useViewport();
// Returns: { width, height, isMobile, isTablet, isDesktop }
```

## 🔊 Adding Sound Effects

1. Place audio files in `client/public/sounds/`
2. Update `AudioManager.js` preloadSounds():

```javascript
const soundFiles = {
  mySound: '/sounds/my-sound.mp3',
  ...
};
```

3. Use in components:

```javascript
audioManager.play('mySound');
```

## 🎨 Adding Sprite Sheets

1. Create sprite sheet (see `client/src/animations/README.md`)
2. Save as `miner-sprites.png` in `client/src/animations/`
3. Set `useSpriteSheet={true}` in MinerSprite component

## 🧪 Testing

All components include:
- Responsive design testing
- Performance optimization
- Accessibility compliance
- Cross-browser compatibility

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Mobile browsers supported with optimized performance.

## 🎯 Quality Levels

The app automatically adjusts based on device capabilities:

| Quality | FPS | Particles | Effects | Use Case |
|---------|-----|-----------|---------|----------|
| High    | 60  | 30        | All     | Desktop |
| Medium  | 30  | 15        | Reduced | Mobile  |
| Low     | 20  | 5         | Minimal | Low-end |

## 🔧 Customization

### Changing Colors

Edit CSS files in `client/src/components/` to customize:
- Glow colors
- Gradient colors
- Border colors
- Shadow effects

### Animation Speed

Adjust animation durations in component props or CSS:
- Particle duration
- Transition speeds
- Sprite frame rates

### Performance Tuning

Modify `client/src/utils/performanceOptimizer.js`:
- FPS targets
- Particle counts
- Quality thresholds

## 📄 License

MIT

## 🙏 Acknowledgments

- React team for the amazing framework
- react-spring for smooth animations
- react-toastify for notifications
- Open source community for inspiration

## 📞 Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ for engaging game experiences**
