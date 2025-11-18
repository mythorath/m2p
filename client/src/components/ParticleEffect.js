import React, { useRef, useEffect, useState } from 'react';

/**
 * Reusable particle system for various visual effects
 * Supports coins, sparkles, and explosion effects
 * Canvas-based rendering with performance optimizations
 */

const ParticleEffect = ({
  type = 'sparkle',
  x = 0,
  y = 0,
  count = 20,
  duration = 1000,
  onComplete = () => {},
  active = true,
  width = 300,
  height = 300
}) => {
  const canvasRef = useRef(null);
  const particlesRef = useRef([]);
  const animationFrameRef = useRef(null);
  const startTimeRef = useRef(null);

  // Particle configurations for different types
  const particleConfigs = {
    coin: {
      color: ['#FFD700', '#FFA500', '#FFFF00'],
      size: [8, 12],
      velocity: { x: [-2, 2], y: [-5, -2] },
      gravity: 0.3,
      rotation: true,
      glow: true
    },
    sparkle: {
      color: ['#FFFFFF', '#FFFF99', '#FFCC00'],
      size: [2, 6],
      velocity: { x: [-3, 3], y: [-3, 3] },
      gravity: 0.1,
      rotation: false,
      glow: true,
      twinkle: true
    },
    explosion: {
      color: ['#FF4500', '#FF6347', '#FFD700', '#FF8C00'],
      size: [4, 10],
      velocity: { x: [-5, 5], y: [-5, 5] },
      gravity: 0.2,
      rotation: true,
      glow: true,
      fade: true
    },
    dust: {
      color: ['#8B7355', '#A0826D', '#B8956A'],
      size: [1, 3],
      velocity: { x: [-1, 1], y: [-2, -1] },
      gravity: 0.05,
      rotation: false,
      glow: false,
      fade: true
    }
  };

  // Initialize particles
  useEffect(() => {
    if (!active) return;

    const config = particleConfigs[type] || particleConfigs.sparkle;
    const particles = [];

    for (let i = 0; i < count; i++) {
      particles.push({
        x: x,
        y: y,
        vx: randomBetween(config.velocity.x[0], config.velocity.x[1]),
        vy: randomBetween(config.velocity.y[0], config.velocity.y[1]),
        size: randomBetween(config.size[0], config.size[1]),
        color: config.color[Math.floor(Math.random() * config.color.length)],
        rotation: config.rotation ? Math.random() * Math.PI * 2 : 0,
        rotationSpeed: config.rotation ? randomBetween(-0.2, 0.2) : 0,
        alpha: 1,
        life: 1,
        twinkle: config.twinkle ? Math.random() * Math.PI * 2 : 0
      });
    }

    particlesRef.current = particles;
    startTimeRef.current = Date.now();
  }, [active, type, x, y, count]);

  // Animation loop
  useEffect(() => {
    if (!active) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const config = particleConfigs[type] || particleConfigs.sparkle;

    const animate = () => {
      const elapsed = Date.now() - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Update and draw particles
      let aliveParticles = 0;

      particlesRef.current.forEach((particle) => {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.vy += config.gravity;

        // Update rotation
        if (config.rotation) {
          particle.rotation += particle.rotationSpeed;
        }

        // Update life/alpha
        particle.life = 1 - progress;
        if (config.fade) {
          particle.alpha = particle.life;
        }

        // Update twinkle
        if (config.twinkle) {
          particle.twinkle += 0.1;
          particle.alpha = 0.5 + Math.sin(particle.twinkle) * 0.5;
        }

        // Check if particle is still alive
        if (particle.life > 0 && particle.alpha > 0) {
          aliveParticles++;

          // Draw particle
          ctx.save();
          ctx.globalAlpha = particle.alpha;
          ctx.translate(particle.x, particle.y);
          ctx.rotate(particle.rotation);

          // Add glow effect
          if (config.glow) {
            ctx.shadowBlur = 10;
            ctx.shadowColor = particle.color;
          }

          // Draw based on type
          if (type === 'coin') {
            // Draw coin as circle with shine
            ctx.fillStyle = particle.color;
            ctx.beginPath();
            ctx.arc(0, 0, particle.size, 0, Math.PI * 2);
            ctx.fill();

            // Add shine
            const gradient = ctx.createRadialGradient(-2, -2, 0, 0, 0, particle.size);
            gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(0, 0, particle.size, 0, Math.PI * 2);
            ctx.fill();
          } else if (type === 'sparkle') {
            // Draw sparkle as star
            ctx.fillStyle = particle.color;
            drawStar(ctx, 0, 0, 5, particle.size, particle.size * 0.5);
          } else {
            // Draw as circle for other types
            ctx.fillStyle = particle.color;
            ctx.beginPath();
            ctx.arc(0, 0, particle.size, 0, Math.PI * 2);
            ctx.fill();
          }

          ctx.restore();
        }
      });

      // Continue animation or complete
      if (progress < 1 && aliveParticles > 0) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        onComplete();
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [active, type, duration, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        position: 'absolute',
        pointerEvents: 'none',
        top: 0,
        left: 0
      }}
    />
  );
};

// Helper functions
function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

function drawStar(ctx, cx, cy, spikes, outerRadius, innerRadius) {
  let rot = Math.PI / 2 * 3;
  let x = cx;
  let y = cy;
  const step = Math.PI / spikes;

  ctx.beginPath();
  ctx.moveTo(cx, cy - outerRadius);

  for (let i = 0; i < spikes; i++) {
    x = cx + Math.cos(rot) * outerRadius;
    y = cy + Math.sin(rot) * outerRadius;
    ctx.lineTo(x, y);
    rot += step;

    x = cx + Math.cos(rot) * innerRadius;
    y = cy + Math.sin(rot) * innerRadius;
    ctx.lineTo(x, y);
    rot += step;
  }

  ctx.lineTo(cx, cy - outerRadius);
  ctx.closePath();
  ctx.fill();
}

export default ParticleEffect;
