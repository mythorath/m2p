"""
Mining History Service for M2P

Fetches historical mining rewards from the blockchain and calculates initial AP
for newly verified players.
"""

import aiohttp
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class MiningHistoryService:
    """
    Service to fetch mining history from blockchain and calculate AP.
    """
    
    # Known mining pool payout addresses
    # These are addresses that send mining rewards to miners
    KNOWN_POOL_ADDRESSES = [
        'ATBxmBJ9974wk3XVZU8my3gcJeYJe7TEkS',  # Primary pool address (observed)
        # Add more as discovered
    ]
    
    # AP conversion rate: 1 ADVC = 10 AP
    ADVC_TO_AP_RATE = 10
    
    def __init__(self, api_base_url: str = 'https://api.adventurecoin.quest'):
        """
        Initialize the mining history service.
        
        Args:
            api_base_url: Base URL for the Adventurecoin API
        """
        self.api_base_url = api_base_url
        self.session = None
    
    async def __aenter__(self):
        """Create aiohttp session."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def fetch_transaction_history(self, wallet_address: str) -> List[str]:
        """
        Fetch all transaction IDs for a wallet.
        
        Args:
            wallet_address: The wallet address to check
            
        Returns:
            List of transaction IDs
        """
        try:
            url = f'{self.api_base_url}/history/{wallet_address}'
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to fetch history for {wallet_address}: {resp.status}")
                    return []
                
                data = await resp.json()
                tx_list = data.get('result', {}).get('tx', [])
                logger.info(f"Found {len(tx_list)} transactions for {wallet_address}")
                return tx_list
        
        except Exception as e:
            logger.error(f"Error fetching transaction history: {e}")
            return []
    
    async def fetch_transaction_details(self, tx_id: str) -> Optional[Dict]:
        """
        Fetch details for a specific transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction data or None if error
        """
        try:
            url = f'{self.api_base_url}/transaction/{tx_id}'
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch transaction {tx_id[:16]}...: {resp.status}")
                    return None
                
                data = await resp.json()
                return data.get('result')
        
        except Exception as e:
            logger.error(f"Error fetching transaction {tx_id[:16]}...: {e}")
            return None
    
    def is_mining_reward(self, tx_data: Dict, wallet_address: str) -> Tuple[bool, Decimal]:
        """
        Determine if a transaction is a mining reward and extract the amount.
        
        A transaction is considered a mining reward if:
        1. It's a coinbase transaction (direct mining), OR
        2. It's sent from a known pool payout address
        
        Args:
            tx_data: Transaction data from API
            wallet_address: The wallet address to check for
            
        Returns:
            Tuple of (is_mining_reward, amount_received)
        """
        try:
            # Check if this is a coinbase transaction (direct mining)
            if tx_data['vin'] and 'coinbase' in tx_data['vin'][0]:
                # Find the amount sent to the wallet
                for vout in tx_data['vout']:
                    addresses = vout.get('scriptPubKey', {}).get('addresses', [])
                    if wallet_address in addresses:
                        amount = Decimal(str(vout['value'])) / Decimal('100000000')
                        logger.info(f"Found coinbase mining reward: {amount} ADVC")
                        return True, amount
            
            # Check if sent from known pool address
            if tx_data['vin']:
                sender_address = None
                
                # Extract sender address from first input
                vin = tx_data['vin'][0]
                if 'scriptPubKey' in vin and 'addresses' in vin['scriptPubKey']:
                    sender_address = vin['scriptPubKey']['addresses'][0]
                
                # Check if sender is a known pool
                if sender_address and sender_address in self.KNOWN_POOL_ADDRESSES:
                    # Find amount sent to the wallet
                    for vout in tx_data['vout']:
                        addresses = vout.get('scriptPubKey', {}).get('addresses', [])
                        if wallet_address in addresses:
                            amount = Decimal(str(vout['value'])) / Decimal('100000000')
                            logger.info(f"Found pool payout from {sender_address[:20]}...: {amount} ADVC")
                            return True, amount
            
            return False, Decimal('0')
        
        except Exception as e:
            logger.error(f"Error checking if mining reward: {e}")
            return False, Decimal('0')
    
    async def fetch_mining_history(self, wallet_address: str, 
                                   max_transactions: int = None) -> List[Dict]:
        """
        Fetch all mining rewards for a wallet from blockchain history.
        
        Args:
            wallet_address: The wallet address to check
            max_transactions: Maximum number of transactions to check (None = all)
            
        Returns:
            List of mining reward events with amount, timestamp, txid, source
        """
        mining_rewards = []
        
        # Get transaction list
        tx_list = await self.fetch_transaction_history(wallet_address)
        
        if max_transactions:
            tx_list = tx_list[:max_transactions]
        
        logger.info(f"Checking {len(tx_list)} transactions for mining rewards...")
        
        # Check each transaction
        for i, tx_id in enumerate(tx_list):
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(tx_list)} transactions checked")
            
            tx_data = await self.fetch_transaction_details(tx_id)
            if not tx_data:
                continue
            
            is_mining, amount = self.is_mining_reward(tx_data, wallet_address)
            
            if is_mining and amount > 0:
                # Determine source (coinbase vs pool)
                source = 'coinbase' if 'coinbase' in tx_data['vin'][0] else 'pool'
                
                # Get pool address if applicable
                pool_address = None
                if source == 'pool' and tx_data['vin']:
                    vin = tx_data['vin'][0]
                    if 'scriptPubKey' in vin and 'addresses' in vin['scriptPubKey']:
                        pool_address = vin['scriptPubKey']['addresses'][0]
                
                mining_rewards.append({
                    'amount_advc': amount,
                    'timestamp': datetime.fromtimestamp(tx_data.get('blocktime', 0)),
                    'txid': tx_id,
                    'source': source,
                    'pool_address': pool_address
                })
        
        logger.info(f"Found {len(mining_rewards)} mining rewards totaling "
                   f"{sum(r['amount_advc'] for r in mining_rewards):.4f} ADVC")
        
        return mining_rewards
    
    def calculate_ap_from_mining(self, mining_rewards: List[Dict]) -> int:
        """
        Calculate total AP from mining rewards.
        
        Args:
            mining_rewards: List of mining reward events
            
        Returns:
            Total AP earned
        """
        total_advc = sum(reward['amount_advc'] for reward in mining_rewards)
        total_ap = int(total_advc * self.ADVC_TO_AP_RATE)
        
        logger.info(f"Calculated {total_ap} AP from {total_advc:.4f} ADVC "
                   f"(rate: 1 ADVC = {self.ADVC_TO_AP_RATE} AP)")
        
        return total_ap
    
    async def process_new_verification(self, wallet_address: str, 
                                      max_history: int = 1000) -> Tuple[int, Decimal, List[Dict]]:
        """
        Process a newly verified wallet and calculate initial AP from mining history.
        
        Args:
            wallet_address: The verified wallet address
            max_history: Maximum number of transactions to check
            
        Returns:
            Tuple of (total_ap, total_advc, mining_rewards_list)
        """
        logger.info(f"Processing mining history for newly verified wallet: {wallet_address}")
        
        # Fetch mining history
        mining_rewards = await self.fetch_mining_history(wallet_address, max_history)
        
        # Calculate totals
        total_advc = sum(reward['amount_advc'] for reward in mining_rewards)
        total_ap = self.calculate_ap_from_mining(mining_rewards)
        
        logger.info(f"Verification complete for {wallet_address}:")
        logger.info(f"  Mining Rewards: {len(mining_rewards)}")
        logger.info(f"  Total ADVC: {total_advc:.4f}")
        logger.info(f"  Total AP: {total_ap}")
        
        return total_ap, total_advc, mining_rewards


async def test_mining_history(wallet_address: str):
    """Test function to check mining history for a wallet."""
    async with MiningHistoryService() as service:
        total_ap, total_advc, rewards = await service.process_new_verification(
            wallet_address, 
            max_history=50  # Check last 50 transactions for testing
        )
        
        print(f"\n{'='*60}")
        print(f"Mining History for {wallet_address}")
        print(f"{'='*60}")
        print(f"Total Mining Rewards Found: {len(rewards)}")
        print(f"Total ADVC Mined: {total_advc:.4f}")
        print(f"Total AP Earned: {total_ap}")
        print(f"\nRecent Mining Rewards:")
        for i, reward in enumerate(rewards[:10], 1):
            print(f"  {i}. {reward['amount_advc']:.4f} ADVC from {reward['source']} "
                  f"at {reward['timestamp']}")
        
        if len(rewards) > 10:
            print(f"  ... and {len(rewards) - 10} more")


if __name__ == '__main__':
    # Test with user's wallet
    import sys
    wallet = sys.argv[1] if len(sys.argv) > 1 else 'AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG'
    asyncio.run(test_mining_history(wallet))
