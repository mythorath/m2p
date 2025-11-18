"""
M2P Wallet Verification Service
Checks blockchain for verification donations and updates player status
"""
import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
import threading

from sqlalchemy.orm import Session
from server.models import Player, VerificationLog
from server.config import (
    DEV_WALLET_ADDRESS,
    VERIFICATION_TIMEOUT_HOURS,
    VERIFICATION_CHECK_INTERVAL_MINUTES,
    MIN_CONFIRMATIONS,
    AP_REFUND_MULTIPLIER,
    ADVC_EXPLORER_API,
    ADVC_EXPLORER_WEB,
    POOL_API_URL,
    API_TIMEOUT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WalletVerifier:
    """
    Wallet verification service that checks blockchain for verification donations
    Uses multiple verification methods with fallback support
    """

    def __init__(self, db_session: Session, socketio=None):
        """
        Initialize wallet verifier

        Args:
            db_session: SQLAlchemy database session
            socketio: SocketIO instance for real-time notifications
        """
        self.db = db_session
        self.socketio = socketio
        self.dev_wallet = DEV_WALLET_ADDRESS
        self.verification_methods = [
            ('advc_explorer_api', self._verify_via_explorer_api),
            ('pool_payment_history', self._verify_via_pool_api),
            ('web_scraping', self._verify_via_web_scraping)
        ]
        self.running = False
        self.verification_thread = None
        logger.info(f"WalletVerifier initialized with dev wallet: {self.dev_wallet}")

    def _verify_via_explorer_api(self, player: Player) -> Optional[str]:
        """
        Method 1: Verify via ADVC Explorer API

        Args:
            player: Player object to verify

        Returns:
            Transaction hash if verified, None otherwise
        """
        logger.info(f"Attempting Explorer API verification for {player.wallet_address}")

        try:
            # Try different API endpoint patterns
            endpoints = [
                f"{ADVC_EXPLORER_API}/transactions/{self.dev_wallet}",
                f"{ADVC_EXPLORER_API}/address/{self.dev_wallet}/txs",
                f"{ADVC_EXPLORER_API}/api/transactions/{self.dev_wallet}",
                f"{ADVC_EXPLORER_API}/api/address/{self.dev_wallet}"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=API_TIMEOUT)
                    if response.status_code == 200:
                        data = response.json()

                        # Parse transaction data (format may vary)
                        transactions = self._parse_transaction_response(data)

                        # Search for matching transaction
                        tx_hash = self._find_matching_transaction(
                            transactions,
                            player.wallet_address,
                            player.verification_amount
                        )

                        if tx_hash:
                            logger.info(f"Found matching transaction via API: {tx_hash}")
                            return tx_hash

                except requests.exceptions.RequestException as e:
                    logger.debug(f"API endpoint {endpoint} failed: {e}")
                    continue

            logger.warning("No API endpoints returned valid data")
            return None

        except Exception as e:
            logger.error(f"Explorer API verification failed: {e}", exc_info=True)
            return None

    def _verify_via_pool_api(self, player: Player) -> Optional[str]:
        """
        Method 2: Verify via Pool Payment History API

        Args:
            player: Player object to verify

        Returns:
            Transaction hash if verified, None otherwise
        """
        logger.info(f"Attempting Pool API verification for {player.wallet_address}")

        try:
            # Try different pool API endpoints
            endpoints = [
                f"{POOL_API_URL}/payments",
                f"{POOL_API_URL}/payments/{self.dev_wallet}",
                f"{POOL_API_URL}/transactions"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=API_TIMEOUT)
                    if response.status_code == 200:
                        data = response.json()

                        # Parse payment data
                        payments = self._parse_payment_response(data)

                        # Search for matching payment
                        tx_hash = self._find_matching_transaction(
                            payments,
                            player.wallet_address,
                            player.verification_amount
                        )

                        if tx_hash:
                            logger.info(f"Found matching transaction via Pool API: {tx_hash}")
                            return tx_hash

                except requests.exceptions.RequestException as e:
                    logger.debug(f"Pool API endpoint {endpoint} failed: {e}")
                    continue

            logger.warning("No Pool API endpoints returned valid data")
            return None

        except Exception as e:
            logger.error(f"Pool API verification failed: {e}", exc_info=True)
            return None

    def _verify_via_web_scraping(self, player: Player) -> Optional[str]:
        """
        Method 3: Verify via Web Scraping (fallback)

        Args:
            player: Player object to verify

        Returns:
            Transaction hash if verified, None otherwise
        """
        logger.info(f"Attempting web scraping verification for {player.wallet_address}")

        try:
            # Scrape the explorer website
            url = f"{ADVC_EXPLORER_WEB}/address/{self.dev_wallet}"

            response = requests.get(url, timeout=API_TIMEOUT)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch explorer page: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Parse transaction table (HTML structure may vary)
            transactions = self._parse_transaction_table(soup)

            # Search for matching transaction
            tx_hash = self._find_matching_transaction(
                transactions,
                player.wallet_address,
                player.verification_amount
            )

            if tx_hash:
                logger.info(f"Found matching transaction via web scraping: {tx_hash}")
                return tx_hash

            logger.warning("No matching transaction found via web scraping")
            return None

        except Exception as e:
            logger.error(f"Web scraping verification failed: {e}", exc_info=True)
            return None

    def _parse_transaction_response(self, data: Dict) -> List[Dict]:
        """
        Parse transaction response from API (handles various formats)

        Args:
            data: JSON response from API

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        try:
            # Handle different response formats
            if isinstance(data, list):
                transactions = data
            elif 'transactions' in data:
                transactions = data['transactions']
            elif 'txs' in data:
                transactions = data['txs']
            elif 'data' in data:
                if isinstance(data['data'], list):
                    transactions = data['data']
                elif 'transactions' in data['data']:
                    transactions = data['data']['transactions']

            # Normalize transaction format
            normalized = []
            for tx in transactions:
                normalized.append({
                    'hash': tx.get('hash') or tx.get('tx_hash') or tx.get('txid'),
                    'from': tx.get('from') or tx.get('sender') or tx.get('source'),
                    'to': tx.get('to') or tx.get('recipient') or tx.get('destination'),
                    'amount': float(tx.get('amount') or tx.get('value') or 0),
                    'confirmations': int(tx.get('confirmations') or 0),
                    'timestamp': tx.get('timestamp') or tx.get('time')
                })

            return normalized

        except Exception as e:
            logger.error(f"Failed to parse transaction response: {e}", exc_info=True)
            return []

    def _parse_payment_response(self, data: Dict) -> List[Dict]:
        """
        Parse payment response from Pool API

        Args:
            data: JSON response from Pool API

        Returns:
            List of payment dictionaries
        """
        # Similar to transaction parsing but for pool payment format
        return self._parse_transaction_response(data)

    def _parse_transaction_table(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse transaction table from HTML

        Args:
            soup: BeautifulSoup object of explorer page

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        try:
            # Find transaction table (selectors may need adjustment)
            table = soup.find('table', {'class': ['transactions', 'tx-table', 'table']})

            if not table:
                logger.warning("Could not find transaction table in HTML")
                return []

            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        # Extract transaction data (adjust indices based on actual HTML)
                        tx_hash = cells[0].get_text().strip()
                        from_addr = cells[1].get_text().strip() if len(cells) > 1 else ''
                        to_addr = cells[2].get_text().strip() if len(cells) > 2 else ''
                        amount_text = cells[3].get_text().strip() if len(cells) > 3 else '0'

                        # Parse amount (remove currency symbol if present)
                        amount = float(amount_text.replace('ADVC', '').replace(',', '').strip())

                        transactions.append({
                            'hash': tx_hash,
                            'from': from_addr,
                            'to': to_addr,
                            'amount': amount,
                            'confirmations': MIN_CONFIRMATIONS,  # Assume confirmed if on explorer
                            'timestamp': None
                        })
                    except (ValueError, AttributeError) as e:
                        logger.debug(f"Failed to parse table row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Failed to parse transaction table: {e}", exc_info=True)

        return transactions

    def _find_matching_transaction(
        self,
        transactions: List[Dict],
        from_wallet: str,
        expected_amount: float
    ) -> Optional[str]:
        """
        Find transaction matching verification criteria

        Args:
            transactions: List of transaction dictionaries
            from_wallet: Expected sender wallet address
            expected_amount: Expected donation amount

        Returns:
            Transaction hash if found, None otherwise
        """
        for tx in transactions:
            try:
                # Check if transaction matches criteria
                tx_from = (tx.get('from') or '').lower()
                tx_to = (tx.get('to') or '').lower()
                tx_amount = float(tx.get('amount') or 0)
                tx_confirmations = int(tx.get('confirmations') or 0)

                # Verify sender, recipient, amount, and confirmations
                if (tx_from == from_wallet.lower() and
                    tx_to == self.dev_wallet.lower() and
                    abs(tx_amount - expected_amount) < 0.0001 and  # Float comparison tolerance
                    tx_confirmations >= MIN_CONFIRMATIONS):

                    return tx.get('hash')

            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to check transaction: {e}")
                continue

        return None

    def verify_donation(self, player: Player) -> bool:
        """
        Verify a player's donation using all available methods

        Args:
            player: Player object to verify

        Returns:
            True if verified successfully, False otherwise
        """
        logger.info(f"Starting verification for player {player.wallet_address}")

        # Check if verification has expired
        if self._is_verification_expired(player):
            logger.warning(f"Verification expired for {player.wallet_address}")
            self._log_verification(
                player,
                'expired',
                'expired',
                error_message='Verification challenge expired (24h timeout)'
            )

            # Notify player of expiration
            if self.socketio:
                self.socketio.emit('verification_expired', {
                    'wallet_address': player.wallet_address,
                    'message': 'Verification challenge expired. Please register again.'
                }, room=player.wallet_address)

            return False

        # Try each verification method in order
        for method_name, method_func in self.verification_methods:
            try:
                logger.info(f"Trying verification method: {method_name}")
                tx_hash = method_func(player)

                if tx_hash:
                    # Verification successful
                    self.mark_verified(player, tx_hash, method_name)
                    return True
                else:
                    logger.info(f"Method {method_name} did not find transaction")

            except Exception as e:
                logger.error(f"Verification method {method_name} failed: {e}", exc_info=True)
                self._log_verification(
                    player,
                    method_name,
                    'error',
                    error_message=str(e)
                )
                continue

        # All methods failed
        logger.warning(f"All verification methods failed for {player.wallet_address}")
        return False

    def _is_verification_expired(self, player: Player) -> bool:
        """
        Check if verification challenge has expired

        Args:
            player: Player object

        Returns:
            True if expired, False otherwise
        """
        if not player.verification_requested_at:
            return True

        expiration_time = player.verification_requested_at + timedelta(hours=VERIFICATION_TIMEOUT_HOURS)
        return datetime.utcnow() > expiration_time

    def mark_verified(self, player: Player, tx_hash: str, method: str = 'manual'):
        """
        Mark player as verified and credit AP refund

        Args:
            player: Player object
            tx_hash: Transaction hash from blockchain
            method: Verification method used
        """
        logger.info(f"Marking player {player.wallet_address} as verified")

        try:
            # Calculate AP refund
            ap_refund = player.verification_amount * AP_REFUND_MULTIPLIER

            # Update player record
            player.verified = True
            player.verification_tx_hash = tx_hash
            player.verification_completed_at = datetime.utcnow()
            player.total_ap += ap_refund

            # Commit changes
            self.db.commit()

            # Log verification
            self._log_verification(
                player,
                method,
                'success',
                tx_hash=tx_hash,
                amount=player.verification_amount,
                ap_credited=ap_refund
            )

            # Emit WebSocket notification
            if self.socketio:
                self.socketio.emit('verification_complete', {
                    'wallet_address': player.wallet_address,
                    'tx_hash': tx_hash,
                    'ap_credited': ap_refund,
                    'total_ap': player.total_ap,
                    'message': f'Verification successful! {ap_refund} AP credited.'
                }, room=player.wallet_address)

            logger.info(f"Player {player.wallet_address} verified successfully. {ap_refund} AP credited.")

        except Exception as e:
            logger.error(f"Failed to mark player as verified: {e}", exc_info=True)
            self.db.rollback()
            raise

    def _log_verification(
        self,
        player: Player,
        method: str,
        status: str,
        tx_hash: Optional[str] = None,
        amount: Optional[float] = None,
        ap_credited: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """
        Log verification attempt to database

        Args:
            player: Player object
            method: Verification method used
            status: Status of verification (success, failed, expired, error)
            tx_hash: Transaction hash if found
            amount: Verification amount
            ap_credited: AP amount credited
            error_message: Error message if failed
        """
        try:
            log = VerificationLog(
                player_id=player.id,
                wallet_address=player.wallet_address,
                verification_method=method,
                status=status,
                tx_hash=tx_hash,
                amount=amount or player.verification_amount,
                ap_credited=ap_credited,
                error_message=error_message
            )
            self.db.add(log)
            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to log verification: {e}", exc_info=True)
            self.db.rollback()

    def check_pending_verifications(self):
        """
        Check all pending verifications and process them
        This runs periodically to check for new transactions
        """
        logger.info("Checking pending verifications...")

        try:
            # Query all unverified players with verification amount set
            pending_players = self.db.query(Player).filter(
                Player.verified == False,
                Player.verification_amount.isnot(None),
                Player.verification_requested_at.isnot(None)
            ).all()

            logger.info(f"Found {len(pending_players)} pending verifications")

            for player in pending_players:
                try:
                    # Skip if already expired
                    if self._is_verification_expired(player):
                        logger.info(f"Skipping expired verification for {player.wallet_address}")
                        continue

                    # Try to verify
                    self.verify_donation(player)

                except Exception as e:
                    logger.error(f"Error processing player {player.wallet_address}: {e}", exc_info=True)
                    continue

            logger.info("Pending verifications check completed")

        except Exception as e:
            logger.error(f"Failed to check pending verifications: {e}", exc_info=True)

    def verification_loop(self):
        """
        Background loop that periodically checks for pending verifications
        Runs every VERIFICATION_CHECK_INTERVAL_MINUTES
        """
        logger.info("Starting verification loop...")
        self.running = True

        while self.running:
            try:
                self.check_pending_verifications()

                # Sleep for configured interval
                sleep_seconds = VERIFICATION_CHECK_INTERVAL_MINUTES * 60
                logger.info(f"Sleeping for {VERIFICATION_CHECK_INTERVAL_MINUTES} minutes...")

                # Sleep in small increments to allow for clean shutdown
                for _ in range(sleep_seconds):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error in verification loop: {e}", exc_info=True)
                # Continue running even on errors
                time.sleep(60)  # Wait 1 minute before retrying

        logger.info("Verification loop stopped")

    def start_verification_loop(self):
        """Start the verification loop in a background thread"""
        if self.verification_thread and self.verification_thread.is_alive():
            logger.warning("Verification loop already running")
            return

        self.verification_thread = threading.Thread(
            target=self.verification_loop,
            daemon=True,
            name="VerificationLoop"
        )
        self.verification_thread.start()
        logger.info("Verification loop thread started")

    def stop_verification_loop(self):
        """Stop the verification loop"""
        logger.info("Stopping verification loop...")
        self.running = False

        if self.verification_thread:
            self.verification_thread.join(timeout=10)
            logger.info("Verification loop stopped")

    def query_advc_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """
        Query ADVC transactions for a specific address

        Args:
            address: Wallet address to query
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries
        """
        logger.info(f"Querying transactions for address: {address}")

        try:
            # Try API endpoints
            endpoints = [
                f"{ADVC_EXPLORER_API}/transactions/{address}?limit={limit}",
                f"{ADVC_EXPLORER_API}/address/{address}/txs?limit={limit}",
                f"{ADVC_EXPLORER_API}/api/transactions?address={address}&limit={limit}"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=API_TIMEOUT)
                    if response.status_code == 200:
                        data = response.json()
                        transactions = self._parse_transaction_response(data)

                        # Filter by recipient address
                        filtered = [
                            tx for tx in transactions
                            if (tx.get('to') or '').lower() == address.lower()
                        ]

                        return filtered[:limit]

                except requests.exceptions.RequestException as e:
                    logger.debug(f"Transaction query endpoint {endpoint} failed: {e}")
                    continue

            logger.warning("Could not query transactions from any API endpoint")
            return []

        except Exception as e:
            logger.error(f"Failed to query transactions: {e}", exc_info=True)
            return []
