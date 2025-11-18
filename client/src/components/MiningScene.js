import React, { useState, useEffect, useRef, useCallback } from 'react';
import MinerSprite from './MinerSprite';
import ParticleEffect from './ParticleEffect';
import './MiningScene.css';

/**
 * Main mining game scene with animations
 * Features:
 * - Animated miner with state-based animations
 * - Dynamic mine environment with parallax layers
 * - Ore veins with sparkle effects
 * - Particle effects based on player activity
 * - Real-time mining rate visualization
 * - Ore glow intensity based on pending rewards
 */

const MiningScene = ({
  miningRate = 0,
  pendingRewards = 0,
  onMine = () => {},
  isActive = false,
  efficiency = 1.0,
  achievements = [],
  width = 800,
  height = 600
}) => {
  const [minerState, setMinerState] = useState('idle');
  const [particles, setParticles] = useState([]);
  const [oreGlow, setOreGlow] = useState(0);
  const [showCelebration, setShowCelebration] = useState(false);
  const canvasRef = useRef(null);
  const parallaxRef = useRef({ layer1: 0, layer2: 0, layer3: 0 });
  const animationFrameRef = useRef(null);
  const particleIdCounter = useRef(0);

  // Update miner state based on activity
  useEffect(() => {
    if (showCelebration) {
      setMinerState('celebrating');
      const timer = setTimeout(() => {
        setShowCelebration(false);
        setMinerState(isActive ? 'mining' : 'idle');
      }, 2000);
      return () => clearTimeout(timer);
    } else {
      setMinerState(isActive ? 'mining' : 'idle');
    }
  }, [isActive, showCelebration]);

  // Update ore glow based on pending rewards
  useEffect(() => {
    const glowIntensity = Math.min(pendingRewards / 100, 1);
    setOreGlow(glowIntensity);
  }, [pendingRewards]);

  // Trigger celebration on achievement unlock
  useEffect(() => {
    if (achievements.length > 0) {
      setShowCelebration(true);
      addParticle('explosion', 400, 300);
    }
  }, [achievements.length]);

  // Add mining particles when active
  useEffect(() => {
    if (!isActive || miningRate === 0) return;

    const interval = setInterval(() => {
      // Add sparkle particles at ore vein locations
      addParticle('sparkle', 500 + Math.random() * 100, 350 + Math.random() * 50);
      addParticle('dust', 480 + Math.random() * 140, 340 + Math.random() * 60);
    }, 500);

    return () => clearInterval(interval);
  }, [isActive, miningRate]);

  // Add particle helper
  const addParticle = useCallback((type, x, y, count = 20) => {
    const id = particleIdCounter.current++;
    setParticles(prev => [...prev, { id, type, x, y, count, active: true }]);
  }, []);

  // Remove particle when complete
  const removeParticle = useCallback((id) => {
    setParticles(prev => prev.filter(p => p.id !== id));
  }, []);

  // Render mine environment
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationId;

    const renderMineEnvironment = (timestamp) => {
      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Parallax scrolling effect
      parallaxRef.current.layer1 = (timestamp * 0.01) % width;
      parallaxRef.current.layer2 = (timestamp * 0.02) % width;
      parallaxRef.current.layer3 = (timestamp * 0.03) % width;

      // Draw background layers (parallax)
      drawParallaxLayer(ctx, parallaxRef.current.layer1, '#1a1a2e', 0.3);
      drawParallaxLayer(ctx, parallaxRef.current.layer2, '#16213e', 0.5);
      drawParallaxLayer(ctx, parallaxRef.current.layer3, '#0f3460', 0.7);

      // Draw mine floor
      ctx.fillStyle = '#2d2d44';
      ctx.fillRect(0, height * 0.7, width, height * 0.3);

      // Draw ore veins
      drawOreVeins(ctx, timestamp);

      // Draw mining efficiency indicator
      drawEfficiencyMeter(ctx);

      animationId = requestAnimationFrame(renderMineEnvironment);
    };

    animationId = requestAnimationFrame(renderMineEnvironment);

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [width, height, oreGlow, efficiency]);

  // Draw parallax background layer
  const drawParallaxLayer = (ctx, offset, color, alpha) => {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = color;

    // Draw repeating pattern
    for (let x = -width; x < width * 2; x += 100) {
      const y = Math.sin((x + offset) * 0.01) * 20 + height * 0.5;
      ctx.fillRect(x, y, 80, height - y);
    }

    ctx.restore();
  };

  // Draw ore veins with glow effect
  const drawOreVeins = (ctx, timestamp) => {
    const ores = [
      { x: 500, y: 350, size: 60 },
      { x: 300, y: 400, size: 40 },
      { x: 650, y: 380, size: 50 }
    ];

    ores.forEach((ore, index) => {
      const pulse = Math.sin(timestamp * 0.003 + index) * 0.3 + 0.7;
      const glowSize = ore.size * (1 + oreGlow * 0.5);

      // Draw glow
      const gradient = ctx.createRadialGradient(ore.x, ore.y, 0, ore.x, ore.y, glowSize);
      gradient.addColorStop(0, `rgba(255, 215, 0, ${oreGlow * pulse})`);
      gradient.addColorStop(0.5, `rgba(255, 165, 0, ${oreGlow * 0.5 * pulse})`);
      gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(ore.x, ore.y, glowSize, 0, Math.PI * 2);
      ctx.fill();

      // Draw ore
      ctx.fillStyle = '#FFD700';
      ctx.strokeStyle = '#FFA500';
      ctx.lineWidth = 2;

      ctx.beginPath();
      ctx.arc(ore.x, ore.y, ore.size * pulse, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Add sparkle points
      if (oreGlow > 0.3) {
        for (let i = 0; i < 3; i++) {
          const angle = (timestamp * 0.002 + i * Math.PI * 2 / 3);
          const sparkleX = ore.x + Math.cos(angle) * ore.size * 0.7;
          const sparkleY = ore.y + Math.sin(angle) * ore.size * 0.7;

          ctx.fillStyle = '#FFFFFF';
          ctx.beginPath();
          ctx.arc(sparkleX, sparkleY, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    });
  };

  // Draw efficiency meter
  const drawEfficiencyMeter = (ctx) => {
    const meterX = 20;
    const meterY = height - 60;
    const meterWidth = 200;
    const meterHeight = 30;

    // Background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(meterX, meterY, meterWidth, meterHeight);

    // Fill based on efficiency
    const fillWidth = meterWidth * Math.min(efficiency, 1);
    const gradient = ctx.createLinearGradient(meterX, 0, meterX + fillWidth, 0);

    if (efficiency < 0.3) {
      gradient.addColorStop(0, '#ff4444');
      gradient.addColorStop(1, '#ff6666');
    } else if (efficiency < 0.7) {
      gradient.addColorStop(0, '#ffaa00');
      gradient.addColorStop(1, '#ffcc00');
    } else {
      gradient.addColorStop(0, '#00ff00');
      gradient.addColorStop(1, '#00cc00');
    }

    ctx.fillStyle = gradient;
    ctx.fillRect(meterX, meterY, fillWidth, meterHeight);

    // Border
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.strokeRect(meterX, meterY, meterWidth, meterHeight);

    // Label
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px monospace';
    ctx.fillText(`Efficiency: ${(efficiency * 100).toFixed(0)}%`, meterX, meterY - 5);
  };

  // Handle click to mine
  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if clicked on ore vein
    const ores = [
      { x: 500, y: 350, size: 60 },
      { x: 300, y: 400, size: 40 },
      { x: 650, y: 380, size: 50 }
    ];

    const clickedOre = ores.find(ore => {
      const distance = Math.sqrt((x - ore.x) ** 2 + (y - ore.y) ** 2);
      return distance < ore.size;
    });

    if (clickedOre) {
      addParticle('sparkle', clickedOre.x, clickedOre.y, 30);
      addParticle('coin', clickedOre.x, clickedOre.y, 10);
      onMine();
    }
  };

  return (
    <div className="mining-scene" style={{ width, height }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="mining-background"
        onClick={handleClick}
      />

      {/* Miner sprite */}
      <div className="miner-container" style={{ left: 200, top: height * 0.5 }}>
        <MinerSprite state={minerState} size={100} />
      </div>

      {/* Mining rate display */}
      <div className="mining-rate-display">
        <div className="rate-label">Mining Rate</div>
        <div className="rate-value">{miningRate.toFixed(2)} AP/s</div>
      </div>

      {/* Particle effects */}
      {particles.map(particle => (
        <ParticleEffect
          key={particle.id}
          type={particle.type}
          x={particle.x}
          y={particle.y}
          count={particle.count}
          active={particle.active}
          width={width}
          height={height}
          onComplete={() => removeParticle(particle.id)}
        />
      ))}

      {/* Pending rewards indicator */}
      {pendingRewards > 0 && (
        <div className="pending-rewards">
          <span className="pending-icon">💎</span>
          <span className="pending-value">+{pendingRewards}</span>
        </div>
      )}
    </div>
  );
};

export default MiningScene;
