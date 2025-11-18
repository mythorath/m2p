import React, { useEffect, useState } from 'react';
import './MinerSprite.css';

/**
 * Animated miner sprite component
 * Supports multiple animation states: idle, mining, celebrating
 * Uses CSS sprite animation for performance
 * Fallback to CSS-only animations if sprite sheet is not available
 */

const MinerSprite = ({
  state = 'idle',
  size = 64,
  useSpriteSheet = false,
  className = ''
}) => {
  const [currentFrame, setCurrentFrame] = useState(0);

  // Animation frame counts and speeds for each state
  const animationConfig = {
    idle: { frames: 4, speed: 500 },    // Breathing animation
    mining: { frames: 6, speed: 150 },  // Pickaxe swing
    celebrating: { frames: 8, speed: 200 } // Victory dance
  };

  // Animate frames for sprite sheet mode
  useEffect(() => {
    if (!useSpriteSheet) return;

    const config = animationConfig[state] || animationConfig.idle;
    const interval = setInterval(() => {
      setCurrentFrame((prev) => (prev + 1) % config.frames);
    }, config.speed);

    return () => clearInterval(interval);
  }, [state, useSpriteSheet]);

  if (useSpriteSheet) {
    // Use sprite sheet (when available)
    const config = animationConfig[state] || animationConfig.idle;
    const frameWidth = 64;
    const frameHeight = 64;
    const row = state === 'idle' ? 0 : state === 'mining' ? 1 : 2;

    return (
      <div
        className={`miner-sprite sprite-sheet ${className}`}
        style={{
          width: size,
          height: size,
          backgroundImage: 'url(/animations/miner-sprites.png)',
          backgroundPosition: `-${currentFrame * frameWidth}px -${row * frameHeight}px`,
          backgroundSize: `${frameWidth * config.frames}px ${frameHeight * 3}px`,
          imageRendering: 'pixelated'
        }}
      />
    );
  }

  // Fallback to CSS-only animations
  return (
    <div
      className={`miner-sprite css-animation ${state} ${className}`}
      style={{ width: size, height: size }}
    >
      <div className="miner-body">
        <div className="miner-head"></div>
        <div className="miner-torso"></div>
        {state === 'mining' && <div className="miner-pickaxe"></div>}
        <div className="miner-arm-left"></div>
        <div className="miner-arm-right"></div>
        <div className="miner-leg-left"></div>
        <div className="miner-leg-right"></div>
      </div>
    </div>
  );
};

export default MinerSprite;
