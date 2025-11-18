import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import { getPlayer } from '../services/api';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useGame();

  const [walletAddress, setWalletAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/game');
    }
  }, [isAuthenticated, navigate]);

  /**
   * Validate wallet address format
   * Basic validation for Dogecoin addresses (starts with D, 34 chars)
   */
  const validateWallet = (wallet) => {
    if (!wallet || wallet.trim().length === 0) {
      return 'Wallet address is required';
    }

    // Basic Dogecoin address validation
    const trimmed = wallet.trim();
    if (trimmed.length < 26 || trimmed.length > 34) {
      return 'Invalid wallet address length';
    }

    if (!trimmed.startsWith('D') && !trimmed.startsWith('A') && !trimmed.startsWith('9')) {
      return 'Invalid Dogecoin wallet address';
    }

    return null;
  };

  /**
   * Handle login form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate wallet
    const validationError = validateWallet(walletAddress);
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      // Check if player exists
      const result = await getPlayer(walletAddress.trim());

      if (result.success && result.data) {
        // Player exists, log them in
        login(walletAddress.trim());
        navigate('/game');
      } else {
        // Player doesn't exist
        setError('Player not found. Please register first.');
      }
    } catch (err) {
      setError('Failed to login. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle wallet address input change
   */
  const handleWalletChange = (e) => {
    setWalletAddress(e.target.value);
    setError(''); // Clear error on input change
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>Mine to Play</h1>
          <p className="tagline">Adventure awaits in the depths</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="wallet">Dogecoin Wallet Address</label>
            <input
              type="text"
              id="wallet"
              value={walletAddress}
              onChange={handleWalletChange}
              placeholder="Enter your wallet address"
              disabled={loading}
              autoComplete="off"
              autoFocus
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !walletAddress.trim()}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="login-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/register" className="link">
              Register here
            </Link>
          </p>
        </div>

        <div className="info-section">
          <h3>How it works:</h3>
          <ol>
            <li>Register with your Dogecoin wallet address</li>
            <li>Verify ownership by sending a small donation</li>
            <li>Your mining activity generates ADVC rewards automatically</li>
            <li>Earn Adventure Points (AP) and unlock achievements</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default Login;
