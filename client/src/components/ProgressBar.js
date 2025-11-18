import React from 'react';
import { useSpring, animated } from 'react-spring';
import './ProgressBar.css';

/**
 * Animated progress bar component
 * Features:
 * - Smooth fill animation
 * - Gradient backgrounds
 * - Multiple variants (achievement, mining, health, etc.)
 * - Optional label and percentage display
 * - Customizable colors
 */

const ProgressBar = ({
  value = 0,
  max = 100,
  variant = 'default',
  label = '',
  showPercentage = true,
  height = '24px',
  animated: isAnimated = true,
  className = '',
  color = null,
  backgroundColor = '#2d2d44'
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  // Animated progress value
  const props = useSpring({
    width: isAnimated ? `${percentage}%` : `${percentage}%`,
    config: { tension: 280, friction: 60 }
  });

  // Color schemes for different variants
  const colorSchemes = {
    default: {
      gradient: ['#4CAF50', '#45a049'],
      glow: '#4CAF50'
    },
    achievement: {
      gradient: ['#FFD700', '#FFA500'],
      glow: '#FFD700'
    },
    mining: {
      gradient: ['#00BFFF', '#1E90FF'],
      glow: '#00BFFF'
    },
    health: {
      gradient: ['#ff4444', '#cc0000'],
      glow: '#ff4444'
    },
    energy: {
      gradient: ['#FFEB3B', '#FFC107'],
      glow: '#FFEB3B'
    },
    experience: {
      gradient: ['#9C27B0', '#7B1FA2'],
      glow: '#9C27B0'
    }
  };

  const scheme = colorSchemes[variant] || colorSchemes.default;
  const fillColor = color || scheme.gradient;

  return (
    <div className={`progress-bar-container ${className}`}>
      {label && (
        <div className="progress-bar-header">
          <span className="progress-bar-label">{label}</span>
          {showPercentage && (
            <span className="progress-bar-percentage">
              {percentage.toFixed(0)}%
            </span>
          )}
        </div>
      )}

      <div
        className="progress-bar-track"
        style={{
          height: height,
          backgroundColor: backgroundColor
        }}
      >
        <animated.div
          className={`progress-bar-fill ${variant}`}
          style={{
            width: props.width,
            background: Array.isArray(fillColor)
              ? `linear-gradient(90deg, ${fillColor[0]}, ${fillColor[1]})`
              : fillColor,
            boxShadow: `0 0 10px ${scheme.glow}`
          }}
        >
          <div className="progress-bar-shine" />
        </animated.div>

        {/* Value display inside bar */}
        {!showPercentage && value !== undefined && (
          <div className="progress-bar-value">
            {value} / {max}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
