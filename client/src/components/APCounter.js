import React, { useEffect, useRef, useState } from 'react';
import { useSpring, animated } from 'react-spring';
import './APCounter.css';

/**
 * Animated Action Points (AP) Counter
 * Features:
 * - Smooth number increment animations
 * - Glow effect on value change
 * - Support for large numbers with formatting
 * - Configurable animation duration
 */

const APCounter = ({
  value = 0,
  label = 'AP',
  fontSize = '2rem',
  glowColor = '#FFD700',
  duration = 1000,
  formatNumber = true,
  decimals = 0,
  prefix = '',
  suffix = '',
  className = ''
}) => {
  const [isGlowing, setIsGlowing] = useState(false);
  const previousValue = useRef(value);

  // Animated value using react-spring
  const { number } = useSpring({
    from: { number: previousValue.current },
    number: value,
    config: { duration: duration }
  });

  // Trigger glow effect when value changes
  useEffect(() => {
    if (value !== previousValue.current) {
      setIsGlowing(true);
      const timer = setTimeout(() => setIsGlowing(false), 500);
      previousValue.current = value;
      return () => clearTimeout(timer);
    }
  }, [value]);

  // Format large numbers with K, M, B suffixes
  const formatLargeNumber = (num) => {
    if (!formatNumber) return num.toFixed(decimals);

    const absNum = Math.abs(num);

    if (absNum >= 1e9) {
      return (num / 1e9).toFixed(1) + 'B';
    } else if (absNum >= 1e6) {
      return (num / 1e6).toFixed(1) + 'M';
    } else if (absNum >= 1e3) {
      return (num / 1e3).toFixed(1) + 'K';
    }

    return num.toFixed(decimals);
  };

  return (
    <div className={`ap-counter ${className}`}>
      {label && <div className="ap-counter-label">{label}</div>}
      <animated.div
        className={`ap-counter-value ${isGlowing ? 'glowing' : ''}`}
        style={{
          fontSize: fontSize,
          '--glow-color': glowColor
        }}
      >
        {prefix}
        {number.to(n => formatLargeNumber(n))}
        {suffix}
      </animated.div>
    </div>
  );
};

export default APCounter;
