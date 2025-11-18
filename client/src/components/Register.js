import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerPlayer, verifyPlayer } from '../services/api';
import './Register.css';

const Register = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState(1); // 1: registration, 2: verification
  const [walletAddress, setWalletAddress] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [challenge, setChallenge] = useState(null);
  const [txid, setTxid] = useState('');
  const [copied, setCopied] = useState({ amount: false, address: false });

  /**
   * Validate wallet address format
   */
  const validateWallet = (wallet) => {
    if (!wallet || wallet.trim().length === 0) {
      return 'Wallet address is required';
    }

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
   * Validate display name
   */
  const validateDisplayName = (name) => {
    if (!name || name.trim().length === 0) {
      return 'Display name is required';
    }

    if (name.trim().length < 3) {
      return 'Display name must be at least 3 characters';
    }

    if (name.trim().length > 30) {
      return 'Display name must be at most 30 characters';
    }

    return null;
  };

  /**
   * Handle registration form submission
   */
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    const walletError = validateWallet(walletAddress);
    if (walletError) {
      setError(walletError);
      return;
    }

    const nameError = validateDisplayName(displayName);
    if (nameError) {
      setError(nameError);
      return;
    }

    setLoading(true);

    try {
      const result = await registerPlayer(walletAddress.trim(), displayName.trim());

      if (result.success) {
        // Move to verification step
        setChallenge(result.data.challenge);
        setStep(2);
      } else {
        setError(result.error || 'Registration failed. Please try again.');
      }
    } catch (err) {
      setError('Registration failed. Please try again.');
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle verification submission
   */
  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');

    if (!txid.trim()) {
      setError('Transaction ID is required');
      return;
    }

    setLoading(true);

    try {
      const result = await verifyPlayer(walletAddress.trim(), txid.trim());

      if (result.success) {
        // Verification successful, navigate to login
        alert('Verification successful! You can now login.');
        navigate('/');
      } else {
        setError(result.error || 'Verification failed. Please check your transaction ID.');
      }
    } catch (err) {
      setError('Verification failed. Please try again.');
      console.error('Verification error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Copy text to clipboard
   */
  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied({ ...copied, [field]: true });
      setTimeout(() => {
        setCopied({ ...copied, [field]: false });
      }, 2000);
    });
  };

  /**
   * Calculate time remaining
   */
  const getTimeRemaining = () => {
    if (!challenge || !challenge.expires_at) return 'N/A';

    const now = Date.now();
    const expiresAt = new Date(challenge.expires_at).getTime();
    const remaining = expiresAt - now;

    if (remaining <= 0) return 'Expired';

    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);

    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <div className="register-header">
          <h1>Create Account</h1>
          <p className="tagline">Join the mining adventure</p>
        </div>

        {step === 1 ? (
          // Registration Step
          <form onSubmit={handleRegister} className="register-form">
            <div className="form-group">
              <label htmlFor="wallet">Dogecoin Wallet Address</label>
              <input
                type="text"
                id="wallet"
                value={walletAddress}
                onChange={(e) => {
                  setWalletAddress(e.target.value);
                  setError('');
                }}
                placeholder="Enter your wallet address"
                disabled={loading}
                autoComplete="off"
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="displayName">Display Name</label>
              <input
                type="text"
                id="displayName"
                value={displayName}
                onChange={(e) => {
                  setDisplayName(e.target.value);
                  setError('');
                }}
                placeholder="Choose a display name"
                disabled={loading}
                autoComplete="off"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !walletAddress.trim() || !displayName.trim()}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
        ) : (
          // Verification Step
          <div className="verification-section">
            <div className="verification-info">
              <h3>Verify Your Wallet</h3>
              <p>
                To verify ownership of your wallet, please send the exact amount shown below
                to the donation address. This is a one-time verification.
              </p>
            </div>

            <div className="challenge-details">
              <div className="challenge-item">
                <label>Amount to Send:</label>
                <div className="challenge-value">
                  <span className="amount">{challenge?.amount || 'N/A'} DOGE</span>
                  <button
                    type="button"
                    className="btn-copy"
                    onClick={() => copyToClipboard(challenge?.amount?.toString() || '', 'amount')}
                  >
                    {copied.amount ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>

              <div className="challenge-item">
                <label>Donation Address:</label>
                <div className="challenge-value">
                  <span className="address">{challenge?.donation_address || 'N/A'}</span>
                  <button
                    type="button"
                    className="btn-copy"
                    onClick={() => copyToClipboard(challenge?.donation_address || '', 'address')}
                  >
                    {copied.address ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>

              <div className="challenge-item">
                <label>Time Remaining:</label>
                <div className="challenge-value">
                  <span className="time">{getTimeRemaining()}</span>
                </div>
              </div>
            </div>

            <form onSubmit={handleVerify} className="verify-form">
              <div className="form-group">
                <label htmlFor="txid">Transaction ID (TXID)</label>
                <input
                  type="text"
                  id="txid"
                  value={txid}
                  onChange={(e) => {
                    setTxid(e.target.value);
                    setError('');
                  }}
                  placeholder="Paste transaction ID here"
                  disabled={loading}
                  autoComplete="off"
                />
                <small>Enter the TXID after sending the donation</small>
              </div>

              {error && <div className="error-message">{error}</div>}

              <button type="submit" className="btn-primary" disabled={loading || !txid.trim()}>
                {loading ? 'Verifying...' : 'Verify Transaction'}
              </button>
            </form>

            <div className="verify-note">
              <p>
                <strong>Note:</strong> Verification may take a few moments. Make sure you send
                the exact amount from your registered wallet address.
              </p>
            </div>
          </div>
        )}

        <div className="register-footer">
          <p>
            Already have an account?{' '}
            <Link to="/" className="link">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
