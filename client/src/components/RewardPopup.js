import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './RewardPopup.css';

const RewardPopup = ({ show, data, onClose }) => {
  // Auto-dismiss after 5 seconds
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  if (!data) return null;

  const {
    advc_amount,
    ap_reward,
    pool_name,
    total_advc,
    total_ap,
  } = data;

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="reward-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="reward-popup"
            initial={{ scale: 0, rotate: -180 }}
            animate={{
              scale: 1,
              rotate: 0,
              transition: {
                type: "spring",
                stiffness: 260,
                damping: 20
              }
            }}
            exit={{
              scale: 0,
              opacity: 0,
              transition: {
                duration: 0.3
              }
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Diamond Icon */}
            <motion.div
              className="reward-icon"
              animate={{
                rotate: [0, -10, 10, -10, 10, 0],
                scale: [1, 1.1, 1, 1.1, 1],
              }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                repeatDelay: 1,
              }}
            >
              💎
            </motion.div>

            {/* Title */}
            <motion.h2
              className="reward-title"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              Mining Reward!
            </motion.h2>

            {/* ADVC Amount */}
            <motion.div
              className="reward-amount advc"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                delay: 0.3,
                type: "spring",
                stiffness: 200,
                damping: 10
              }}
            >
              <span className="plus">+</span>
              <span className="value">{parseFloat(advc_amount).toFixed(8)}</span>
              <span className="currency">ADVC</span>
            </motion.div>

            {/* AP Amount */}
            <motion.div
              className="reward-amount ap"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                delay: 0.4,
                type: "spring",
                stiffness: 200,
                damping: 10
              }}
            >
              <span className="plus">+</span>
              <span className="value">{ap_reward}</span>
              <span className="currency">AP</span>
            </motion.div>

            {/* Pool Name */}
            <motion.div
              className="reward-pool"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              From pool: <strong>{pool_name}</strong>
            </motion.div>

            {/* Totals */}
            <motion.div
              className="reward-totals"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <div className="total-item">
                <span className="total-label">Total ADVC:</span>
                <span className="total-value">{parseFloat(total_advc || 0).toFixed(8)}</span>
              </div>
              <div className="total-item">
                <span className="total-label">Total AP:</span>
                <span className="total-value">{total_ap || 0}</span>
              </div>
            </motion.div>

            {/* Particles/Confetti Effect */}
            <div className="particles">
              {[...Array(20)].map((_, i) => (
                <motion.div
                  key={i}
                  className="particle"
                  initial={{
                    x: 0,
                    y: 0,
                    opacity: 1,
                  }}
                  animate={{
                    x: Math.random() * 400 - 200,
                    y: Math.random() * 400 - 200,
                    opacity: 0,
                  }}
                  transition={{
                    duration: 1.5,
                    delay: Math.random() * 0.5,
                  }}
                  style={{
                    left: '50%',
                    top: '50%',
                  }}
                />
              ))}
            </div>

            {/* Close hint */}
            <motion.div
              className="close-hint"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              Click anywhere to close
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default RewardPopup;
