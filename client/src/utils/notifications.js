import { toast } from 'react-toastify';

/**
 * Notification system wrapper for react-toastify
 * Provides consistent notification styles and behaviors
 * Types: success, info, warning, error
 * Features: auto-dismiss, stackable, positioned top-right
 */

const defaultOptions = {
  position: 'top-right',
  autoClose: 3000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  progress: undefined,
};

export const notify = {
  // Success notifications
  success: (message, options = {}) => {
    toast.success(message, {
      ...defaultOptions,
      ...options,
      className: 'notification-success',
      icon: '✅'
    });
  },

  // Info notifications
  info: (message, options = {}) => {
    toast.info(message, {
      ...defaultOptions,
      ...options,
      className: 'notification-info',
      icon: 'ℹ️'
    });
  },

  // Warning notifications
  warning: (message, options = {}) => {
    toast.warning(message, {
      ...defaultOptions,
      ...options,
      className: 'notification-warning',
      icon: '⚠️'
    });
  },

  // Error notifications
  error: (message, options = {}) => {
    toast.error(message, {
      ...defaultOptions,
      autoClose: 5000,
      ...options,
      className: 'notification-error',
      icon: '❌'
    });
  },

  // Achievement unlock notification
  achievement: (title, description, options = {}) => {
    toast.success(
      <div className="achievement-notification">
        <div className="achievement-icon">🏆</div>
        <div className="achievement-content">
          <div className="achievement-title">{title}</div>
          <div className="achievement-description">{description}</div>
        </div>
      </div>,
      {
        ...defaultOptions,
        autoClose: 5000,
        ...options,
        className: 'notification-achievement'
      }
    );
  },

  // Reward notification
  reward: (amount, type = 'AP', options = {}) => {
    toast.success(
      <div className="reward-notification">
        <div className="reward-icon">💎</div>
        <div className="reward-content">
          <div className="reward-amount">+{amount}</div>
          <div className="reward-type">{type}</div>
        </div>
      </div>,
      {
        ...defaultOptions,
        autoClose: 2000,
        ...options,
        className: 'notification-reward'
      }
    );
  },

  // Mining notification
  mining: (message, options = {}) => {
    toast.info(message, {
      ...defaultOptions,
      autoClose: 2000,
      ...options,
      className: 'notification-mining',
      icon: '⛏️'
    });
  },

  // Custom notification with custom icon
  custom: (message, icon, options = {}) => {
    toast(message, {
      ...defaultOptions,
      ...options,
      icon: icon
    });
  },

  // Promise-based notification (for async operations)
  promise: (promise, messages, options = {}) => {
    return toast.promise(
      promise,
      {
        pending: messages.pending || 'Processing...',
        success: messages.success || 'Success!',
        error: messages.error || 'Something went wrong'
      },
      {
        ...defaultOptions,
        ...options
      }
    );
  }
};

export default notify;
