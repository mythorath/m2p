/**
 * Performance optimization utilities
 * Provides functions for optimizing rendering and animations
 */

/**
 * Throttle function execution
 */
export const throttle = (func, delay) => {
  let lastCall = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return func.apply(this, args);
    }
  };
};

/**
 * Debounce function execution
 */
export const debounce = (func, delay) => {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
};

/**
 * Request animation frame with fallback
 */
export const requestFrame = (() => {
  return (
    window.requestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.mozRequestAnimationFrame ||
    function (callback) {
      return window.setTimeout(callback, 1000 / 60);
    }
  );
})();

/**
 * Cancel animation frame with fallback
 */
export const cancelFrame = (() => {
  return (
    window.cancelAnimationFrame ||
    window.webkitCancelAnimationFrame ||
    window.mozCancelAnimationFrame ||
    function (id) {
      clearTimeout(id);
    }
  );
})();

/**
 * Optimize canvas rendering
 */
export class CanvasOptimizer {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d', {
      alpha: options.alpha ?? true,
      desynchronized: options.desynchronized ?? true,
      willReadFrequently: options.willReadFrequently ?? false
    });

    this.pixelRatio = options.pixelRatio ?? window.devicePixelRatio || 1;
    this.useOffscreenCanvas = options.useOffscreenCanvas ?? false;

    if (this.useOffscreenCanvas && 'OffscreenCanvas' in window) {
      this.offscreenCanvas = new OffscreenCanvas(canvas.width, canvas.height);
      this.offscreenCtx = this.offscreenCanvas.getContext('2d');
    }

    this.setupCanvas();
  }

  setupCanvas() {
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * this.pixelRatio;
    this.canvas.height = rect.height * this.pixelRatio;
    this.ctx.scale(this.pixelRatio, this.pixelRatio);

    if (this.offscreenCtx) {
      this.offscreenCanvas.width = this.canvas.width;
      this.offscreenCanvas.height = this.canvas.height;
      this.offscreenCtx.scale(this.pixelRatio, this.pixelRatio);
    }
  }

  getContext() {
    return this.offscreenCtx || this.ctx;
  }

  render(callback) {
    const ctx = this.getContext();
    callback(ctx);

    if (this.offscreenCtx) {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.drawImage(this.offscreenCanvas, 0, 0);
    }
  }
}

/**
 * Object pool for reusing objects
 */
export class ObjectPool {
  constructor(factory, initialSize = 10) {
    this.factory = factory;
    this.pool = [];
    this.active = new Set();

    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.factory());
    }
  }

  acquire() {
    let obj = this.pool.pop();
    if (!obj) {
      obj = this.factory();
    }
    this.active.add(obj);
    return obj;
  }

  release(obj) {
    if (this.active.has(obj)) {
      this.active.delete(obj);
      this.pool.push(obj);
    }
  }

  releaseAll() {
    this.active.forEach((obj) => this.pool.push(obj));
    this.active.clear();
  }

  getActiveCount() {
    return this.active.size;
  }

  getPoolSize() {
    return this.pool.length;
  }
}

/**
 * FPS monitor
 */
export class FPSMonitor {
  constructor(callback, interval = 1000) {
    this.callback = callback;
    this.interval = interval;
    this.frames = 0;
    this.lastTime = performance.now();
    this.running = false;
    this.animationId = null;
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.measure();
  }

  stop() {
    this.running = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }

  measure = () => {
    if (!this.running) return;

    this.frames++;
    const currentTime = performance.now();
    const delta = currentTime - this.lastTime;

    if (delta >= this.interval) {
      const fps = Math.round((this.frames * 1000) / delta);
      this.callback(fps);
      this.frames = 0;
      this.lastTime = currentTime;
    }

    this.animationId = requestAnimationFrame(this.measure);
  };
}

/**
 * Check if device is low-end
 */
export const isLowEndDevice = () => {
  // Check hardware concurrency (CPU cores)
  const cores = navigator.hardwareConcurrency || 2;

  // Check memory (if available)
  const memory = navigator.deviceMemory || 4;

  // Check if mobile
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );

  return cores <= 2 || memory <= 2 || isMobile;
};

/**
 * Get recommended quality settings
 */
export const getQualitySettings = () => {
  const isLowEnd = isLowEndDevice();
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reducedMotion) {
    return {
      quality: 'low',
      particleCount: 0,
      enableGlow: false,
      enableShadows: false,
      fps: 30
    };
  }

  if (isLowEnd) {
    return {
      quality: 'medium',
      particleCount: 10,
      enableGlow: true,
      enableShadows: false,
      fps: 30
    };
  }

  return {
    quality: 'high',
    particleCount: 30,
    enableGlow: true,
    enableShadows: true,
    fps: 60
  };
};

export default {
  throttle,
  debounce,
  requestFrame,
  cancelFrame,
  CanvasOptimizer,
  ObjectPool,
  FPSMonitor,
  isLowEndDevice,
  getQualitySettings
};
