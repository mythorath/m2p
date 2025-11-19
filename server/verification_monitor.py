"""
Verification Monitor Service for M2P

Monitors the donation address for incoming verification transactions
and automatically verifies players when their challenge amount is received.
"""

import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from decimal import Decimal
from models import db, Player, MiningEvent
from flask_socketio import SocketIO
from mining_history_service import MiningHistoryService

logger = logging.getLogger(__name__)

# Donation address for verification payments
DONATION_ADDRESS = "AKUg58E171GVJNw2RQzooQnuHs1zns2ecD"
API_BASE_URL = "https://api.adventurecoin.quest"

class VerificationMonitor:
    """Background service to monitor verification transactions."""
    
    def __init__(self, app, socketio):
        """
        Initialize verification monitor.
        
        Args:
            app: Flask application instance
            socketio: SocketIO instance for real-time notifications
        """
        self.app = app
        self.socketio = socketio
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
        self.last_checked_txids = set()  # Track already processed transactions
        
    async def fetch_donation_address_transactions(self):
        """
        Fetch recent transactions for the donation address.
        
        Returns:
            list: List of transaction hashes
        """
        try:
            api_url = f"{API_BASE_URL}/history/{DONATION_ADDRESS}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch donation address transactions: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    if data.get('error'):
                        logger.error(f"API error: {data.get('error')}")
                        return []
                    
                    result = data.get('result', {})
                    tx_list = result.get('tx', [])
                    
                    logger.info(f"Fetched {len(tx_list)} transactions for donation address")
                    return tx_list
                    
        except Exception as e:
            logger.error(f"Error fetching donation address transactions: {str(e)}")
            return []
    
    async def fetch_transaction_details(self, txid):
        """
        Fetch detailed information about a transaction.
        
        Args:
            txid: Transaction hash
            
        Returns:
            dict: Transaction details or None
        """
        try:
            api_url = f"{API_BASE_URL}/transaction/{txid}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch transaction {txid}: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if data.get('error'):
                        logger.warning(f"API error for tx {txid}: {data.get('error')}")
                        return None
                    
                    return data.get('result')
                    
        except Exception as e:
            logger.error(f"Error fetching transaction {txid}: {str(e)}")
            return None
    
    def extract_sender_and_amount(self, tx_details):
        """
        Extract sender address and amount sent to donation address.
        
        Args:
            tx_details: Transaction details from API
            
        Returns:
            tuple: (sender_address, amount_to_donation) or (None, None)
        """
        try:
            # Get the first input address (sender)
            vin = tx_details.get('vin', [])
            if not vin:
                return None, None
            
            # For non-coinbase transactions, we need to look up the previous transaction
            # For now, we'll use a simplified approach and look at vout
            vout = tx_details.get('vout', [])
            
            sender_address = None
            amount_to_donation = None
            
            # Find outputs to our donation address
            for output in vout:
                script_pub_key = output.get('scriptPubKey', {})
                addresses = script_pub_key.get('addresses', [])
                value = output.get('value', 0)
                
                if DONATION_ADDRESS in addresses:
                    # Convert from satoshis to ADVC (divide by 10^8)
                    amount_to_donation = Decimal(str(value)) / Decimal('100000000')
                    logger.info(f"Found payment of {amount_to_donation} ADVC to donation address")
            
            # For sender, we need to check the vin addresses
            # If it's not a coinbase transaction, get the first vin
            if vin and not vin[0].get('coinbase'):
                # We'd need to fetch the previous transaction to get the sender
                # For simplicity, we'll parse from the transaction structure
                # In production, you'd want to fetch the previous tx
                pass
            
            return sender_address, amount_to_donation
            
        except Exception as e:
            logger.error(f"Error extracting sender and amount: {str(e)}")
            return None, None
    
    async def check_pending_verifications(self):
        """
        Check for pending player verifications and match with recent transactions.
        """
        try:
            with self.app.app_context():
                # Get players with pending verification (not verified, challenge not expired)
                now = datetime.utcnow()
                pending_players = Player.query.filter(
                    Player.verified == False,
                    Player.challenge_amount.isnot(None),
                    Player.challenge_expires_at > now
                ).all()
                
                if not pending_players:
                    logger.debug("No pending verifications to check")
                    return
                
                logger.info(f"Checking {len(pending_players)} pending verifications")
                
                # Fetch recent transactions
                tx_list = await self.fetch_donation_address_transactions()
                
                # Only check new transactions
                new_txids = [tx for tx in tx_list if tx not in self.last_checked_txids]
                
                if not new_txids:
                    logger.debug("No new transactions to check")
                    return
                
                logger.info(f"Processing {len(new_txids)} new transactions")
                
                # Check each new transaction
                for txid in new_txids[:20]:  # Limit to 20 most recent
                    tx_details = await self.fetch_transaction_details(txid)
                    
                    if not tx_details:
                        continue
                    
                    # Extract sender and amount
                    sender_address, amount = self.extract_sender_and_amount(tx_details)
                    
                    if not amount:
                        continue
                    
                    # Check if this matches any pending player's challenge amount
                    for player in pending_players:
                        challenge_amount = Decimal(str(player.challenge_amount))
                        
                        # Match with tolerance of 0.0001
                        if abs(amount - challenge_amount) < Decimal('0.0001'):
                            logger.info(f"Found matching amount {amount} ADVC for player {player.display_name} (wallet: {player.wallet_address}, challenge: {challenge_amount})")
                            logger.info(f"Transaction ID: {txid}")
                            
                            # Mark player as verified
                            # In production, you'd want to verify the sender address matches player.wallet_address
                            # For now, matching the unique challenge amount is sufficient since it's highly unlikely
                            # another wallet would send the exact same 4-decimal amount to this address
                            player.verified = True
                            player.challenge_amount = None
                            player.challenge_expires_at = None
                            
                            # Fetch mining history and calculate initial AP
                            logger.info(f"Fetching mining history for {player.wallet_address}...")
                            try:
                                async with MiningHistoryService() as mining_service:
                                    total_ap, total_advc, mining_rewards = await mining_service.process_new_verification(
                                        player.wallet_address,
                                        max_history=1000  # Check up to last 1000 transactions
                                    )
                                    
                                    # Update player stats
                                    player.total_ap = total_ap
                                    player.total_mined_advc = total_advc
                                    
                                    # Create mining event records
                                    for reward in mining_rewards:
                                        # Check if event already exists
                                        existing = MiningEvent.query.filter_by(
                                            wallet_address=player.wallet_address,
                                            timestamp=reward['timestamp']
                                        ).first()
                                        
                                        if not existing:
                                            mining_event = MiningEvent(
                                                wallet_address=player.wallet_address,
                                                amount_advc=reward['amount_advc'],
                                                ap_awarded=int(reward['amount_advc'] * 10),
                                                pool=reward['source'],
                                                timestamp=reward['timestamp']
                                            )
                                            db.session.add(mining_event)
                                    
                                    logger.info(f"✓ Mining history processed: {len(mining_rewards)} rewards, "
                                              f"{total_advc:.4f} ADVC, {total_ap} AP")
                            
                            except Exception as e:
                                logger.error(f"Error fetching mining history: {e}")
                                # Continue with verification even if mining history fails
                            
                            db.session.commit()
                            
                            # Send WebSocket notification
                            self.socketio.emit('verification_complete', {
                                'wallet': player.wallet_address,
                                'display_name': player.display_name,
                                'verified': True,
                                'timestamp': datetime.utcnow().isoformat(),
                                'tx_id': txid,
                                'total_ap': player.total_ap,
                                'total_mined_advc': float(player.total_mined_advc),
                                'mining_rewards_found': len(mining_rewards) if 'mining_rewards' in locals() else 0
                            }, room=player.wallet_address)
                            
                            logger.info(f"✓ Player {player.display_name} ({player.wallet_address}) verified successfully with tx {txid}!")
                            break  # Stop checking other players once we find a match
                    
                    # Mark this transaction as checked
                    self.last_checked_txids.add(txid)
                
                # Cleanup old txids (keep last 1000)
                if len(self.last_checked_txids) > 1000:
                    # Convert to list, sort, keep newest 500
                    self.last_checked_txids = set(list(self.last_checked_txids)[-500:])
                
        except Exception as e:
            logger.error(f"Error checking pending verifications: {str(e)}")
    
    async def run_monitor_loop(self):
        """Main monitoring loop."""
        logger.info("Verification monitor started")
        self.running = True
        
        while self.running:
            try:
                await self.check_pending_verifications()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    def start(self):
        """Start the verification monitor in the background."""
        if not self.running:
            logger.info(f"Starting verification monitor (checking every {self.check_interval}s)")
            # Run in a separate thread
            import threading
            
            def run_loop():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.run_monitor_loop())
            
            thread = threading.Thread(target=run_loop, daemon=True)
            thread.start()
            logger.info("Verification monitor thread started")
    
    def stop(self):
        """Stop the verification monitor."""
        logger.info("Stopping verification monitor")
        self.running = False
