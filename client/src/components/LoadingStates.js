import React from 'react';
import './LoadingStates.css';

/**
 * Loading state components collection
 * - Spinner: Classic spinning loader
 * - Skeleton: Content placeholder with shimmer
 * - ProgressBar: Determinate loading indicator
 * - Dots: Animated dot loader
 * - Pulse: Pulsing circle loader
 */

// Spinner component
export const Spinner = ({ size = 40, color = '#FFD700', className = '' }) => {
  return (
    <div className={`spinner ${className}`} style={{ width: size, height: size }}>
      <div
        className="spinner-circle"
        style={{
          borderColor: `${color}33`,
          borderTopColor: color,
          width: size,
          height: size,
          borderWidth: size / 8
        }}
      />
    </div>
  );
};

// Skeleton loader component
export const Skeleton = ({
  width = '100%',
  height = '20px',
  borderRadius = '4px',
  count = 1,
  className = ''
}) => {
  return (
    <div className={`skeleton-container ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="skeleton"
          style={{
            width,
            height,
            borderRadius,
            marginBottom: index < count - 1 ? '8px' : '0'
          }}
        >
          <div className="skeleton-shimmer" />
        </div>
      ))}
    </div>
  );
};

// Skeleton card (common layout)
export const SkeletonCard = ({ className = '' }) => {
  return (
    <div className={`skeleton-card ${className}`}>
      <Skeleton width="60%" height="24px" />
      <Skeleton width="100%" height="16px" count={3} />
      <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
        <Skeleton width="80px" height="32px" />
        <Skeleton width="80px" height="32px" />
      </div>
    </div>
  );
};

// Animated dots loader
export const DotsLoader = ({ color = '#FFD700', size = 12, className = '' }) => {
  return (
    <div className={`dots-loader ${className}`}>
      <div
        className="dot"
        style={{ backgroundColor: color, width: size, height: size }}
      />
      <div
        className="dot"
        style={{ backgroundColor: color, width: size, height: size }}
      />
      <div
        className="dot"
        style={{ backgroundColor: color, width: size, height: size }}
      />
    </div>
  );
};

// Pulse loader
export const PulseLoader = ({ size = 60, color = '#FFD700', className = '' }) => {
  return (
    <div className={`pulse-loader ${className}`} style={{ width: size, height: size }}>
      <div
        className="pulse-circle"
        style={{
          width: size,
          height: size,
          backgroundColor: color
        }}
      />
      <div
        className="pulse-ring"
        style={{
          width: size,
          height: size,
          borderColor: color
        }}
      />
    </div>
  );
};

// Progress circle
export const ProgressCircle = ({
  progress = 0,
  size = 100,
  strokeWidth = 8,
  color = '#FFD700',
  backgroundColor = '#2d2d44',
  showPercentage = true,
  className = ''
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className={`progress-circle ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        {/* Background circle */}
        <circle
          className="progress-circle-bg"
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="none"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        {/* Progress circle */}
        <circle
          className="progress-circle-fg"
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          r={radius}
          cx={size / 2}
          cy={size / 2}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      {showPercentage && (
        <div className="progress-circle-text" style={{ color }}>
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
};

// Loading overlay
export const LoadingOverlay = ({
  loading = false,
  message = 'Loading...',
  children,
  type = 'spinner',
  className = ''
}) => {
  if (!loading) return children;

  const loaderComponents = {
    spinner: <Spinner />,
    dots: <DotsLoader />,
    pulse: <PulseLoader />
  };

  return (
    <div className={`loading-overlay-container ${className}`}>
      {children && <div className="loading-overlay-content blurred">{children}</div>}
      <div className="loading-overlay">
        <div className="loading-overlay-inner">
          {loaderComponents[type] || <Spinner />}
          {message && <div className="loading-overlay-message">{message}</div>}
        </div>
      </div>
    </div>
  );
};

// Mining loader (themed for the game)
export const MiningLoader = ({ className = '' }) => {
  return (
    <div className={`mining-loader ${className}`}>
      <div className="mining-loader-pickaxe">⛏️</div>
      <div className="mining-loader-text">Mining...</div>
      <div className="mining-loader-dots">
        <span>.</span>
        <span>.</span>
        <span>.</span>
      </div>
    </div>
  );
};

export default {
  Spinner,
  Skeleton,
  SkeletonCard,
  DotsLoader,
  PulseLoader,
  ProgressCircle,
  LoadingOverlay,
  MiningLoader
};
