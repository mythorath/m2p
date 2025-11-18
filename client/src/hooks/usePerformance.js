import { useState, useEffect } from 'react';

/**
 * Performance optimization hook
 * Detects device capabilities and adjusts rendering accordingly
 * - Detects mobile devices
 * - Checks for reduced motion preference
 * - Monitors FPS
 * - Provides quality settings
 */

export const usePerformance = () => {
  const [performance, setPerformance] = useState({
    isMobile: false,
    reducedMotion: false,
    lowPowerMode: false,
    quality: 'high',
    fps: 60
  });

  useEffect(() => {
    // Detect mobile
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    );

    // Check reduced motion preference
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Check for battery API to detect low power mode
    let lowPowerMode = false;
    if ('getBattery' in navigator) {
      navigator.getBattery().then((battery) => {
        lowPowerMode = battery.charging === false && battery.level < 0.2;
      });
    }

    // Determine quality based on device
    let quality = 'high';
    if (isMobile) {
      quality = 'medium';
    }
    if (reducedMotion || lowPowerMode) {
      quality = 'low';
    }

    setPerformance({
      isMobile,
      reducedMotion,
      lowPowerMode,
      quality,
      fps: 60
    });
  }, []);

  // Monitor FPS
  useEffect(() => {
    if (performance.quality === 'low') return;

    let frameCount = 0;
    let lastTime = performance.now ? performance.now() : Date.now();
    let frameId;

    const measureFPS = (currentTime) => {
      frameCount++;
      const delta = currentTime - lastTime;

      if (delta >= 1000) {
        const fps = Math.round((frameCount * 1000) / delta);

        setPerformance((prev) => ({
          ...prev,
          fps,
          quality: fps < 30 ? 'low' : fps < 50 ? 'medium' : prev.quality
        }));

        frameCount = 0;
        lastTime = currentTime;
      }

      frameId = requestAnimationFrame(measureFPS);
    };

    frameId = requestAnimationFrame(measureFPS);

    return () => {
      if (frameId) {
        cancelAnimationFrame(frameId);
      }
    };
  }, [performance.quality]);

  return performance;
};

/**
 * Hook for responsive animations
 * Returns whether animations should be enabled based on device/preferences
 */
export const useAnimations = () => {
  const performance = usePerformance();

  return {
    enableParticles: !performance.isMobile && !performance.reducedMotion && performance.quality !== 'low',
    enableTransitions: !performance.reducedMotion,
    particleCount: performance.quality === 'high' ? 30 : performance.quality === 'medium' ? 15 : 5,
    enableGlow: performance.quality !== 'low',
    enableShadows: performance.quality === 'high',
    fps: performance.quality === 'high' ? 60 : performance.quality === 'medium' ? 30 : 20
  };
};

/**
 * Hook for detecting viewport size
 */
export const useViewport = () => {
  const [viewport, setViewport] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
    isMobile: window.innerWidth < 768,
    isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
    isDesktop: window.innerWidth >= 1024
  });

  useEffect(() => {
    const handleResize = () => {
      setViewport({
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: window.innerWidth < 768,
        isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
        isDesktop: window.innerWidth >= 1024
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return viewport;
};

/**
 * Hook for throttling frame updates
 */
export const useThrottle = (callback, delay) => {
  const [lastRun, setLastRun] = useState(Date.now());

  return (...args) => {
    const now = Date.now();
    if (now - lastRun >= delay) {
      callback(...args);
      setLastRun(now);
    }
  };
};

export default {
  usePerformance,
  useAnimations,
  useViewport,
  useThrottle
};
