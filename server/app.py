"""
Flask API Server with WebSocket support for M2P (Mining to Play) system.

This server provides REST API endpoints for player management, achievements,
leaderboards, and real-time WebSocket communication for mining events.

Main features:
- Player registration and verification
- Mining event tracking
- Achievement system
- Leaderboard functionality
- AP (Action Points) management
- Real-time WebSocket notifications
"""

import os
import logging
import re
import aiohttp
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError

from models import (
    db, Player, MiningEvent, Achievement, PlayerAchievement,
    Purchase, generate_challenge_amount, Dungeon, DungeonRun,
    PlayerCharacter, Gear, PlayerInventory, Monster
)
from dungeon_service import DungeonService
from verification_monitor import VerificationMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DONATION_ADDRESS = os.environ.get('DONATION_ADDRESS', 'AKUg58E171GVJNw2RQzooQnuHs1zns2ecD')

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///m2p.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = os.environ.get('DEBUG', 'False') == 'True'

# Initialize extensions
db.init_app(app)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
socketio = SocketIO(
    app,
    cors_allowed_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    async_mode='threading'
)

# Rate limiting - Disabled for testing
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[],  # No limits for testing
    storage_uri="memory://"
)

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")

# Initialize dungeon service
dungeon_service = DungeonService(app=app, socketio=socketio)

# Initialize verification monitor
verification_monitor = VerificationMonitor(app=app, socketio=socketio)


# ===========================
# Validation Functions
# ===========================

async def verify_wallet_onchain(wallet):
    """
    Verify wallet exists on Adventurecoin blockchain and has made at least one transaction.
    
    Args:
        wallet: Wallet address to verify
        
    Returns:
        bool: True if wallet exists and has transactions, False otherwise
    """
    try:
        # Use the history endpoint to check if wallet has any transactions
        api_url = f"https://api.adventurecoin.quest/history/{wallet}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    logger.warning(f"Wallet verification failed for {wallet}: API returned {response.status}")
                    return False
                
                data = await response.json()
                
                # Check for error in response
                if data.get('error'):
                    logger.warning(f"Wallet {wallet} verification error: {data.get('error')}")
                    return False
                
                # Check if wallet has transaction history
                result = data.get('result', {})
                tx_count = result.get('txcount', 0)
                tx_list = result.get('tx', [])
                
                if tx_count == 0 or len(tx_list) == 0:
                    logger.warning(f"Wallet {wallet} has no transaction history (txcount: {tx_count})")
                    return False
                
                logger.info(f"Wallet {wallet} verified successfully with {tx_count} transactions")
                return True
                
    except asyncio.TimeoutError:
        logger.error(f"Timeout verifying wallet {wallet}")
        return False
    except Exception as e:
        logger.error(f"Error verifying wallet {wallet}: {str(e)}")
        return False


async def verify_transaction_onchain(tx_hash, sender_wallet, recipient_wallet, expected_amount):
    """
    Verify a specific transaction on the Adventurecoin blockchain.
    
    Args:
        tx_hash: Transaction hash to verify
        sender_wallet: Expected sender wallet address
        recipient_wallet: Expected recipient wallet address
        expected_amount: Expected transaction amount in ADVC
        
    Returns:
        dict: {'valid': bool, 'error': str or None}
    """
    try:
        api_url = f"https://api.adventurecoin.quest/transaction/{tx_hash}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return {'valid': False, 'error': f'Transaction not found or API error (status {response.status})'}
                
                data = await response.json()
                
                if data.get('error'):
                    return {'valid': False, 'error': f'Transaction verification error: {data.get("error")}'}
                
                result = data.get('result', {})
                
                # Verify transaction has confirmations
                confirmations = result.get('confirmations', 0)
                if confirmations < 1:
                    return {'valid': False, 'error': 'Transaction not yet confirmed (needs at least 1 confirmation)'}
                
                # Get transaction outputs (vout)
                vouts = result.get('vout', [])
                
                # Find output to our donation address and verify amount
                found_payment = False
                for vout in vouts:
                    script_pub_key = vout.get('scriptPubKey', {})
                    addresses = script_pub_key.get('addresses', [])
                    value_satoshis = vout.get('value', 0)
                    
                    # Convert satoshis to ADVC (1 ADVC = 100000000 satoshis)
                    value_advc = value_satoshis / 100000000.0
                    
                    if recipient_wallet in addresses:
                        # Check if amount matches (allow small variance for fees)
                        expected_float = float(expected_amount)
                        if abs(value_advc - expected_float) < 0.0001:  # Within 0.0001 ADVC
                            found_payment = True
                            break
                
                if not found_payment:
                    return {'valid': False, 'error': f'Transaction does not contain payment of {expected_amount} ADVC to {recipient_wallet}'}
                
                logger.info(f"Transaction {tx_hash} verified successfully from {sender_wallet}")
                return {'valid': True, 'error': None}
                
    except asyncio.TimeoutError:
        return {'valid': False, 'error': 'Timeout verifying transaction on blockchain'}
    except Exception as e:
        logger.error(f"Error verifying transaction {tx_hash}: {str(e)}")
        return {'valid': False, 'error': f'Error verifying transaction: {str(e)}'}


def validate_wallet_address(wallet, check_blockchain=False):
    """
    Validate Advancecoin wallet address format and optionally verify on blockchain.

    Args:
        wallet: Wallet address to validate
        check_blockchain: Whether to verify wallet exists on blockchain (default: False for backwards compatibility)

    Returns:
        bool: True if valid, False otherwise
    """
    if not wallet or not isinstance(wallet, str):
        return False
    
    # Check format: Wallet should start with 'A' and be 34 characters long
    if not re.match(r'^A[a-zA-Z0-9]{33}$', wallet):
        return False
    
    # If blockchain verification is requested, check on-chain
    if check_blockchain:
        try:
            # Run async verification in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(verify_wallet_onchain(wallet))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in blockchain verification: {str(e)}")
            return False
    
    return True


def validate_positive_number(value, field_name="value"):
    """
    Validate that a number is positive.

    Args:
        value: Number to validate
        field_name: Name of field for error messages

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        num = float(value) if isinstance(value, str) else value
        if num <= 0:
            return False, f"{field_name} must be positive"
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


# ===========================
# Error Handlers
# ===========================

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    logger.warning(f"Bad request: {error}")
    return jsonify({'error': str(error.description) if hasattr(error, 'description') else 'Bad request'}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    logger.warning(f"Not found: {request.url}")
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal error: {error}")
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    db.session.rollback()
    return jsonify({'error': 'An unexpected error occurred'}), 500


# ===========================
# Middleware
# ===========================

@app.before_request
def log_request():
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.path} - {get_remote_address()}")


@app.after_request
def after_request(response):
    """Add additional headers after request."""
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    return response


# ===========================
# Health Check Endpoint
# ===========================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response with service status and database connectivity
    """
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    return jsonify({
        'status': 'ok' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/pending_verifications', methods=['GET'])
def get_pending_verifications():
    """
    Get all pending verifications (for testing/debugging).
    
    Returns:
        JSON response with pending verification details
    """
    try:
        now = datetime.utcnow()
        pending_players = Player.query.filter(
            Player.verified == False,
            Player.challenge_amount.isnot(None),
            Player.challenge_expires_at > now
        ).all()
        
        pending_list = []
        for player in pending_players:
            pending_list.append({
                'wallet_address': player.wallet_address,
                'display_name': player.display_name,
                'challenge_amount': float(player.challenge_amount),
                'expires_at': player.challenge_expires_at.isoformat(),
                'created_at': player.created_at.isoformat()
            })
        
        return jsonify({
            'count': len(pending_list),
            'donation_address': DONATION_ADDRESS,
            'pending_verifications': pending_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching pending verifications: {e}")
        return jsonify({'error': str(e)}), 500


# ===========================
# Player Management Endpoints
# ===========================

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per hour")
def register_player():
    """
    Register a new player.

    Request body:
        {
            "wallet_address": "A...",
            "display_name": "Player Name"
        }

    Returns:
        201: Registration successful
        {
            "challenge_amount": 1.5234,
            "donation_address": "SYSTEM_WALLET_ADDRESS",
            "expires_at": "2025-11-18T12:00:00"
        }
        400: Invalid input
        409: Player already exists
    """
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        wallet_address = data.get('wallet_address', '').strip()
        display_name = data.get('display_name', '').strip()

        if not wallet_address or not display_name:
            return jsonify({'error': 'wallet_address and display_name are required'}), 400

        # Validate wallet format first
        if not validate_wallet_address(wallet_address, check_blockchain=False):
            return jsonify({'error': 'Invalid wallet address format. Must start with A and be 34 characters.'}), 400

        # Verify wallet exists on blockchain with transactions
        if not validate_wallet_address(wallet_address, check_blockchain=True):
            return jsonify({'error': 'Wallet address not found on Adventurecoin blockchain or has no transaction history. Please use a wallet that has made at least one transaction.'}), 400

        if len(display_name) < 3 or len(display_name) > 50:
            return jsonify({'error': 'display_name must be between 3 and 50 characters'}), 400

        # Check if player already exists
        existing_player = Player.query.filter_by(wallet_address=wallet_address).first()
        if existing_player:
            return jsonify({'error': 'Player already registered'}), 409

        # Generate challenge amount and expiration
        challenge_amount = generate_challenge_amount()
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Create new player
        new_player = Player(
            wallet_address=wallet_address,
            display_name=display_name,
            challenge_amount=challenge_amount,
            challenge_expires_at=expires_at,
            verified=False
        )

        db.session.add(new_player)
        db.session.commit()

        logger.info(f"New player registered: {wallet_address} ({display_name})")

        return jsonify({
            'challenge_amount': float(challenge_amount),
            'donation_address': DONATION_ADDRESS,
            'expires_at': expires_at.isoformat()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in register_player: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/player/<wallet>', methods=['GET'])
def get_player(wallet):
    """
    Get player information.

    Args:
        wallet: Player wallet address

    Returns:
        200: Player data
        {
            "wallet_address": "A...",
            "display_name": "Player Name",
            "verified": true,
            "total_ap": 1000,
            "spent_ap": 200,
            "available_ap": 800,
            "total_mined_advc": 123.456,
            "created_at": "2025-11-01T00:00:00",
            "recent_events": [...],
            "achievements_unlocked": 5
        }
        400: Invalid wallet address
        404: Player not found
    """
    try:
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address format'}), 400

        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        return jsonify(player.to_dict(include_events=True, include_achievements=True)), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_player: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/player/<wallet>/verify', methods=['POST'])
@limiter.limit("10 per hour")
def verify_player(wallet):
    """
    Verify player wallet ownership.

    Args:
        wallet: Player wallet address

    Request body:
        {
            "tx_hash": "transaction_hash"
        }

    Returns:
        200: Verification successful
        {
            "verified": true,
            "ap_credited": 150
        }
        400: Invalid input or verification failed
        404: Player not found
    """
    try:
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address format'}), 400

        data = request.get_json()
        if not data or 'tx_hash' not in data:
            return jsonify({'error': 'tx_hash is required'}), 400

        tx_hash = data['tx_hash'].strip()
        if not tx_hash:
            return jsonify({'error': 'tx_hash cannot be empty'}), 400

        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        if player.verified:
            return jsonify({'error': 'Player already verified'}), 400

        # Check if verification challenge has expired
        if player.challenge_expires_at and datetime.utcnow() > player.challenge_expires_at:
            return jsonify({'error': 'Verification challenge expired'}), 400

        # Verify transaction on blockchain
        # Run async blockchain verification
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        verification_result = loop.run_until_complete(
            verify_transaction_onchain(tx_hash, wallet, DONATION_ADDRESS, player.challenge_amount)
        )
        loop.close()
        
        if not verification_result['valid']:
            return jsonify({'error': verification_result['error']}), 400

        # Credit AP (convert challenge amount to AP, e.g., 1 ADVC = 100 AP)
        ap_credited = int(float(player.challenge_amount) * 100)
        player.verified = True
        player.total_ap += ap_credited

        db.session.commit()

        logger.info(f"Player verified: {wallet}, AP credited: {ap_credited}")

        # Emit WebSocket event
        socketio.emit('verification_complete', {
            'ap_refunded': ap_credited
        }, room=wallet)

        return jsonify({
            'verified': True,
            'ap_credited': ap_credited
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in verify_player: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/player/<wallet>/spend-ap', methods=['POST'])
@limiter.limit("20 per hour")
def spend_ap(wallet):
    """
    Spend Action Points.

    Args:
        wallet: Player wallet address

    Request body:
        {
            "amount": 100,
            "item_id": "item_123",
            "item_name": "Power Boost" (optional)
        }

    Returns:
        200: Purchase successful
        {
            "new_balance": 700,
            "spent": 100
        }
        400: Invalid input or insufficient balance
        404: Player not found
    """
    try:
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address format'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        amount = data.get('amount')
        item_id = data.get('item_id', '').strip()

        if not amount or not item_id:
            return jsonify({'error': 'amount and item_id are required'}), 400

        # Validate amount is positive
        is_valid, error_msg = validate_positive_number(amount, 'amount')
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        amount = int(amount)

        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        # Check sufficient balance
        if player.available_ap < amount:
            return jsonify({'error': 'Insufficient AP balance'}), 400

        # Record purchase
        purchase = Purchase(
            wallet_address=wallet,
            amount=amount,
            item_id=item_id,
            item_name=data.get('item_name')
        )

        player.spent_ap += amount

        db.session.add(purchase)
        db.session.commit()

        logger.info(f"AP spent: {wallet} spent {amount} AP on {item_id}")

        return jsonify({
            'new_balance': player.available_ap,
            'spent': amount
        }), 200

    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid amount format'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in spend_ap: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# ===========================
# Leaderboard Endpoints
# ===========================

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get leaderboard rankings.

    Query parameters:
        period: 'all_time', 'week', 'day' (default: 'all_time')
        limit: Number of results (default: 50, max: 100)

    Returns:
        200: Leaderboard data
        [
            {
                "rank": 1,
                "wallet_address": "A...",
                "display_name": "Player Name",
                "total_mined_advc": 1234.567,
                "total_ap": 123456
            },
            ...
        ]
    """
    try:
        period = request.args.get('period', 'all_time')
        limit = min(int(request.args.get('limit', 50)), 100)

        # Build query based on period
        if period == 'day':
            cutoff_time = datetime.utcnow() - timedelta(days=1)
            # Sum mining events in the period
            subquery = db.session.query(
                MiningEvent.wallet_address,
                func.sum(MiningEvent.amount_advc).label('period_mined')
            ).filter(
                MiningEvent.timestamp >= cutoff_time
            ).group_by(
                MiningEvent.wallet_address
            ).subquery()

            query = db.session.query(
                Player,
                subquery.c.period_mined
            ).join(
                subquery,
                Player.wallet_address == subquery.c.wallet_address
            ).order_by(
                desc(subquery.c.period_mined)
            ).limit(limit)

            results = []
            for rank, (player, period_mined) in enumerate(query.all(), 1):
                results.append({
                    'rank': rank,
                    'wallet_address': player.wallet_address,
                    'display_name': player.display_name,
                    'total_mined_advc': float(period_mined) if period_mined else 0,
                    'total_ap': player.total_ap
                })

        elif period == 'week':
            cutoff_time = datetime.utcnow() - timedelta(weeks=1)
            subquery = db.session.query(
                MiningEvent.wallet_address,
                func.sum(MiningEvent.amount_advc).label('period_mined')
            ).filter(
                MiningEvent.timestamp >= cutoff_time
            ).group_by(
                MiningEvent.wallet_address
            ).subquery()

            query = db.session.query(
                Player,
                subquery.c.period_mined
            ).join(
                subquery,
                Player.wallet_address == subquery.c.wallet_address
            ).order_by(
                desc(subquery.c.period_mined)
            ).limit(limit)

            results = []
            for rank, (player, period_mined) in enumerate(query.all(), 1):
                results.append({
                    'rank': rank,
                    'wallet_address': player.wallet_address,
                    'display_name': player.display_name,
                    'total_mined_advc': float(period_mined) if period_mined else 0,
                    'total_ap': player.total_ap
                })

        else:  # all_time
            query = Player.query.order_by(
                desc(Player.total_mined_advc)
            ).limit(limit)

            results = []
            for rank, player in enumerate(query.all(), 1):
                results.append({
                    'rank': rank,
                    'wallet_address': player.wallet_address,
                    'display_name': player.display_name,
                    'total_mined_advc': float(player.total_mined_advc),
                    'total_ap': player.total_ap
                })

        return jsonify(results), 200

    except ValueError:
        return jsonify({'error': 'Invalid limit parameter'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_leaderboard: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/leaderboard/<wallet>/rank', methods=['GET'])
def get_player_rank(wallet):
    """
    Get specific player's leaderboard rank.

    Args:
        wallet: Player wallet address

    Returns:
        200: Player rank
        {
            "rank": 42,
            "total_mined_advc": 123.456,
            "total_players": 1000
        }
        400: Invalid wallet address
        404: Player not found
    """
    try:
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address format'}), 400

        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        # Calculate rank (number of players with more ADVC mined + 1)
        rank = Player.query.filter(
            Player.total_mined_advc > player.total_mined_advc
        ).count() + 1

        total_players = Player.query.count()

        return jsonify({
            'rank': rank,
            'total_mined_advc': float(player.total_mined_advc),
            'total_players': total_players
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_player_rank: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# ===========================
# Achievement Endpoints
# ===========================

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """
    Get all achievements.

    Query parameters:
        wallet: Optional wallet address to include unlock status

    Returns:
        200: List of achievements
        [
            {
                "id": 1,
                "name": "First Mine",
                "description": "Complete your first mining event",
                "ap_reward": 100,
                "icon": "trophy",
                "unlocked": true (if wallet provided),
                "unlocked_at": "2025-11-01T00:00:00" (if unlocked)
            },
            ...
        ]
    """
    try:
        wallet = request.args.get('wallet')

        # Validate wallet if provided
        if wallet and not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address format'}), 400

        achievements = Achievement.query.all()
        results = [achievement.to_dict(player_wallet=wallet) for achievement in achievements]

        return jsonify(results), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_achievements: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/player/<wallet>/achievements', methods=['GET'])
def get_player_achievements(wallet):
    """
    Get player's unlocked achievements.

    Args:
        wallet: Player wallet address

    Returns:
        200: List of unlocked achievements
        [
            {
                "achievement_id": 1,
                "achievement_name": "First Mine",
                "achievement_description": "Complete your first mining event",
                "ap_reward": 100,
                "icon": "trophy",
                "unlocked_at": "2025-11-01T00:00:00"
            },
            ...
        ]
        400: Invalid wallet address
        404: Player not found
    """
    try:
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address format'}), 400

        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        player_achievements = PlayerAchievement.query.filter_by(
            wallet_address=wallet
        ).order_by(
            desc(PlayerAchievement.unlocked_at)
        ).all()

        results = [pa.to_dict() for pa in player_achievements]

        return jsonify(results), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_player_achievements: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# ===========================
# Statistics Endpoint
# ===========================

@app.route('/api/stats', methods=['GET'])
def get_global_stats():
    """
    Get global system statistics.

    Returns:
        200: Global statistics
        {
            "total_players": 1000,
            "verified_players": 800,
            "total_advc_mined": 123456.789,
            "total_ap_awarded": 12345678,
            "total_mining_events": 50000
        }
    """
    try:
        total_players = Player.query.count()
        verified_players = Player.query.filter_by(verified=True).count()

        total_advc_result = db.session.query(
            func.sum(Player.total_mined_advc)
        ).scalar()
        total_advc_mined = float(total_advc_result) if total_advc_result else 0

        total_ap_result = db.session.query(
            func.sum(Player.total_ap)
        ).scalar()
        total_ap_awarded = int(total_ap_result) if total_ap_result else 0

        total_mining_events = MiningEvent.query.count()

        return jsonify({
            'total_players': total_players,
            'verified_players': verified_players,
            'total_advc_mined': total_advc_mined,
            'total_ap_awarded': total_ap_awarded,
            'total_mining_events': total_mining_events
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_global_stats: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# ===========================
# DUNGEON SYSTEM ENDPOINTS
# ===========================

# --- Dungeon Management ---

@app.route('/api/dungeons', methods=['GET'])
@limiter.limit("100 per hour")
def get_dungeons():
    """
    Get list of all available dungeons.

    Query params:
        wallet (optional): Player wallet to check unlock status

    Returns:
        200: List of dungeons with unlock status
    """
    try:
        wallet = request.args.get('wallet')
        dungeons = Dungeon.query.filter_by(active=True).all()

        results = []
        for dungeon in dungeons:
            dungeon_data = dungeon.to_dict(include_stats=True)

            # Check if player meets requirements
            if wallet and validate_wallet_address(wallet):
                player = Player.query.filter_by(wallet_address=wallet).first()
                character = PlayerCharacter.query.filter_by(player_id=wallet).first()

                if character:
                    dungeon_data['can_enter'] = character.level >= dungeon.min_level_required
                    dungeon_data['player_level'] = character.level
                else:
                    dungeon_data['can_enter'] = False
                    dungeon_data['player_level'] = 0

                if player:
                    dungeon_data['can_afford'] = player.available_ap >= dungeon.ap_cost_per_run
                else:
                    dungeon_data['can_afford'] = False

            results.append(dungeon_data)

        return jsonify(results), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_dungeons: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeons/<int:dungeon_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_dungeon_details(dungeon_id):
    """Get detailed information about a specific dungeon."""
    try:
        dungeon = Dungeon.query.get(dungeon_id)
        if not dungeon:
            return jsonify({'error': 'Dungeon not found'}), 404

        dungeon_data = dungeon.to_dict(include_stats=True)

        # Get monsters for this dungeon
        monsters = Monster.query.filter_by(dungeon_id=dungeon_id).all()
        dungeon_data['monsters'] = [m.to_dict() for m in monsters]

        return jsonify(dungeon_data), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_dungeon_details: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/start', methods=['POST'])
@limiter.limit("20 per hour")
def start_dungeon_run():
    """
    Start a new dungeon run.

    Request body:
        {
            "wallet": "A...",
            "dungeon_id": 1
        }

    Returns:
        200: Dungeon run started successfully
        400: Invalid request or requirements not met
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        dungeon_id = data.get('dungeon_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        if not dungeon_id:
            return jsonify({'error': 'Dungeon ID required'}), 400

        # Get player, character, and dungeon
        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        character = PlayerCharacter.query.filter_by(player_id=wallet).first()
        if not character:
            # Create character if doesn't exist
            character = dungeon_service.create_character(wallet)

        dungeon = Dungeon.query.get(dungeon_id)
        if not dungeon or not dungeon.active:
            return jsonify({'error': 'Dungeon not available'}), 404

        # Check requirements
        if character.level < dungeon.min_level_required:
            return jsonify({
                'error': f'Requires level {dungeon.min_level_required}',
                'player_level': character.level
            }), 400

        if player.available_ap < dungeon.ap_cost_per_run:
            return jsonify({
                'error': 'Insufficient AP',
                'required': dungeon.ap_cost_per_run,
                'available': player.available_ap
            }), 400

        # Check for active runs
        active_run = DungeonRun.query.filter_by(
            player_id=wallet,
            status='active'
        ).first()

        if active_run:
            return jsonify({
                'error': 'Already have an active dungeon run',
                'active_run': active_run.to_dict()
            }), 400

        # Spend AP
        player.spent_ap += dungeon.ap_cost_per_run

        # Create dungeon run
        run = DungeonRun(
            player_id=wallet,
            dungeon_id=dungeon_id,
            current_floor=1,
            furthest_floor_reached=1,
            status='active',
            ap_spent=dungeon.ap_cost_per_run,
            player_health=character.health,
        )
        db.session.add(run)
        db.session.commit()

        # Emit WebSocket event
        if socketio:
            socketio.emit('dungeon_started', {
                'run_id': run.id,
                'dungeon_name': dungeon.name,
                'player': player.display_name,
            }, room=wallet)

        logger.info(f"Player {wallet} started dungeon run in {dungeon.name}")

        return jsonify({
            'success': True,
            'run': run.to_dict(),
            'character': character.to_dict(),
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in start_dungeon_run: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/current', methods=['GET'])
@limiter.limit("100 per hour")
def get_current_dungeon_run():
    """
    Get player's current active dungeon run.

    Query params:
        wallet: Player wallet address

    Returns:
        200: Current run data or null
    """
    try:
        wallet = request.args.get('wallet')
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.filter_by(
            player_id=wallet,
            status='active'
        ).first()

        if not run:
            return jsonify({'run': None}), 200

        return jsonify({'run': run.to_dict()}), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_current_dungeon_run: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/abandon', methods=['POST'])
@limiter.limit("20 per hour")
def abandon_dungeon_run():
    """
    Abandon current dungeon run (lose unclaimed loot).

    Request body:
        {
            "wallet": "A...",
            "run_id": 123
        }

    Returns:
        200: Run abandoned successfully
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet:
            return jsonify({'error': 'Run not found'}), 404

        if run.status != 'active':
            return jsonify({'error': 'Run is not active'}), 400

        result = dungeon_service.abandon_dungeon_run(run)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in abandon_dungeon_run: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# --- Combat & Exploration ---

@app.route('/api/dungeon/explore', methods=['POST'])
@limiter.limit("100 per hour")
def explore_dungeon():
    """
    Explore current floor (advance room or floor).

    Request body:
        {
            "wallet": "A...",
            "run_id": 123
        }

    Returns:
        200: Encounter generated (monster/treasure/rest)
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet or run.status != 'active':
            return jsonify({'error': 'Invalid run'}), 404

        # Check if in combat
        if run.combat_state:
            return jsonify({'error': 'Already in combat'}), 400

        # Generate encounter
        encounter = dungeon_service.generate_room_encounter(
            run.dungeon,
            run.current_floor
        )

        run.current_room += 1

        if encounter['type'] == 'monster':
            # Start combat
            monster = Monster.query.get(encounter['monster_id'])
            dungeon_service.start_combat(run, monster)

        elif encounter['type'] == 'rest':
            # Heal player
            character = run.player.character
            heal_amount = int(character.max_health * encounter['heal_percent'])
            character.heal(heal_amount)
            run.player_health = character.health
            encounter['healed'] = heal_amount

        db.session.commit()

        return jsonify({
            'success': True,
            'encounter': encounter,
            'run': run.to_dict(),
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in explore_dungeon: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/combat/attack', methods=['POST'])
@limiter.limit("100 per hour")
def combat_attack():
    """
    Execute combat attack action.

    Request body:
        {
            "wallet": "A...",
            "run_id": 123,
            "action": "attack" | "defend"
        }

    Returns:
        200: Combat turn result
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')
        action = data.get('action', 'attack')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet or run.status != 'active':
            return jsonify({'error': 'Invalid run'}), 404

        if not run.combat_state:
            return jsonify({'error': 'Not in combat'}), 400

        # Execute combat turn
        result = dungeon_service.execute_combat_turn(run, action)

        # Emit WebSocket events
        if socketio and result.get('success'):
            socketio.emit('combat_hit', {
                'run_id': run.id,
                'player_damage': result.get('player_damage_dealt', 0),
                'monster_damage': result.get('monster_damage_dealt', 0),
            }, room=wallet)

            if result.get('victory'):
                socketio.emit('monster_defeated', {
                    'run_id': run.id,
                    'rewards': result.get('rewards'),
                }, room=wallet)

            if result.get('player_defeated'):
                socketio.emit('player_defeated', {
                    'run_id': run.id,
                    'exp_kept': run.total_exp_gained,
                }, room=wallet)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in combat_attack: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/combat/flee', methods=['POST'])
@limiter.limit("100 per hour")
def combat_flee():
    """
    Attempt to flee from combat (60% success rate).

    Request body:
        {
            "wallet": "A...",
            "run_id": 123
        }

    Returns:
        200: Flee attempt result
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet or run.status != 'active':
            return jsonify({'error': 'Invalid run'}), 404

        if not run.combat_state:
            return jsonify({'error': 'Not in combat'}), 400

        result = dungeon_service.execute_combat_turn(run, 'flee')

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in combat_flee: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/advance-floor', methods=['POST'])
@limiter.limit("50 per hour")
def advance_floor():
    """
    Advance to next floor in dungeon.

    Request body:
        {
            "wallet": "A...",
            "run_id": 123
        }

    Returns:
        200: Advanced to next floor
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet or run.status != 'active':
            return jsonify({'error': 'Invalid run'}), 404

        if run.combat_state:
            return jsonify({'error': 'Cannot advance while in combat'}), 400

        result = dungeon_service.advance_floor(run)

        if result['success'] and socketio:
            socketio.emit('floor_cleared', {
                'run_id': run.id,
                'floor': run.current_floor,
            }, room=wallet)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in advance_floor: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# --- Character & Inventory ---

@app.route('/api/character', methods=['GET'])
@limiter.limit("100 per hour")
def get_character():
    """
    Get player's RPG character stats.

    Query params:
        wallet: Player wallet address

    Returns:
        200: Character data
    """
    try:
        wallet = request.args.get('wallet')
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        character = PlayerCharacter.query.filter_by(player_id=wallet).first()

        if not character:
            # Create character if doesn't exist
            character = dungeon_service.create_character(wallet)

        return jsonify(character.to_dict()), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_character: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/inventory', methods=['GET'])
@limiter.limit("100 per hour")
def get_inventory():
    """
    Get player's gear inventory.

    Query params:
        wallet: Player wallet address

    Returns:
        200: List of inventory items
    """
    try:
        wallet = request.args.get('wallet')
        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        inventory = PlayerInventory.query.filter_by(player_id=wallet).all()

        results = [item.to_dict() for item in inventory]

        return jsonify(results), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_inventory: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/inventory/equip/<int:inventory_id>', methods=['POST'])
@limiter.limit("50 per hour")
def equip_gear(inventory_id):
    """
    Equip gear from inventory.

    Request body:
        {
            "wallet": "A..."
        }

    Returns:
        200: Gear equipped successfully
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        character = PlayerCharacter.query.filter_by(player_id=wallet).first()
        if not character:
            return jsonify({'error': 'Character not found'}), 404

        inventory_item = PlayerInventory.query.get(inventory_id)
        if not inventory_item or inventory_item.player_id != wallet:
            return jsonify({'error': 'Item not found'}), 404

        result = dungeon_service.equip_gear(character, inventory_item)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in equip_gear: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/inventory/sell/<int:inventory_id>', methods=['POST'])
@limiter.limit("50 per hour")
def sell_gear(inventory_id):
    """
    Sell gear for AP.

    Request body:
        {
            "wallet": "A..."
        }

    Returns:
        200: Gear sold successfully
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        player = Player.query.filter_by(wallet_address=wallet).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        inventory_item = PlayerInventory.query.get(inventory_id)
        if not inventory_item or inventory_item.player_id != wallet:
            return jsonify({'error': 'Item not found'}), 404

        result = dungeon_service.sell_gear(player, inventory_item)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in sell_gear: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# --- Loot & Rewards ---

@app.route('/api/dungeon/loot/claim', methods=['POST'])
@limiter.limit("50 per hour")
def claim_loot():
    """
    Claim all unclaimed loot from dungeon run.

    Request body:
        {
            "wallet": "A...",
            "run_id": 123
        }

    Returns:
        200: Loot claimed successfully
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet:
            return jsonify({'error': 'Run not found'}), 404

        claimed_gear = dungeon_service.claim_loot(run, wallet)

        # Emit rare loot notifications
        if socketio:
            for gear in claimed_gear:
                if gear.rarity in ['epic', 'legendary']:
                    socketio.emit('loot_dropped', {
                        'player': run.player.display_name,
                        'gear_name': gear.name,
                        'rarity': gear.rarity,
                    }, room=wallet)

        return jsonify({
            'success': True,
            'claimed_count': len(claimed_gear),
            'gear': [g.to_dict() for g in claimed_gear],
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in claim_loot: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/complete', methods=['POST'])
@limiter.limit("50 per hour")
def complete_dungeon():
    """
    Complete dungeon run and claim rewards.

    Request body:
        {
            "wallet": "A...",
            "run_id": 123
        }

    Returns:
        200: Dungeon completed successfully
    """
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        run_id = data.get('run_id')

        if not validate_wallet_address(wallet):
            return jsonify({'error': 'Invalid wallet address'}), 400

        run = DungeonRun.query.get(run_id)
        if not run or run.player_id != wallet or run.status != 'active':
            return jsonify({'error': 'Invalid run'}), 404

        if run.combat_state:
            return jsonify({'error': 'Cannot complete while in combat'}), 400

        result = dungeon_service.complete_dungeon_run(run)

        if socketio:
            socketio.emit('dungeon_completed', {
                'run_id': run.id,
                'dungeon_name': run.dungeon.name,
                'floors_cleared': run.furthest_floor_reached,
                'player': run.player.display_name,
            }, room=wallet)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in complete_dungeon: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


@app.route('/api/dungeon/leaderboard/<int:dungeon_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_dungeon_leaderboard(dungeon_id):
    """
    Get leaderboard for specific dungeon.

    Query params:
        limit: Number of results (default 10, max 100)

    Returns:
        200: Leaderboard data
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)

        leaderboard = dungeon_service.get_dungeon_leaderboard(dungeon_id, limit)

        return jsonify(leaderboard), 200

    except ValueError:
        return jsonify({'error': 'Invalid limit parameter'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_dungeon_leaderboard: {e}")
        return jsonify({'error': 'Database error occurred'}), 500


# ===========================
# WebSocket Event Handlers
# ===========================

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection.

    Logs the connection and sends confirmation.
    """
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    emit('connection_response', {
        'status': 'connected',
        'message': 'Successfully connected to M2P server',
        'timestamp': datetime.utcnow().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.

    Logs the disconnection.
    """
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")


@socketio.on('join')
def handle_join(data):
    """
    Handle client joining a room (wallet-specific notifications).

    Args:
        data: Dictionary containing 'wallet' address

    Emits:
        join_response: Confirmation of room join
    """
    try:
        if not data or 'wallet' not in data:
            emit('error', {'message': 'wallet address is required'})
            return

        wallet = data['wallet'].strip()

        if not validate_wallet_address(wallet):
            emit('error', {'message': 'Invalid wallet address format'})
            return

        # Join room named after wallet address
        join_room(wallet)
        logger.info(f"Client {request.sid} joined room: {wallet}")

        emit('join_response', {
            'status': 'joined',
            'wallet': wallet,
            'message': f'Joined notification room for {wallet}'
        })

    except Exception as e:
        logger.error(f"Error in handle_join: {e}")
        emit('error', {'message': 'Failed to join room'})


@socketio.on('leave')
def handle_leave(data):
    """
    Handle client leaving a room.

    Args:
        data: Dictionary containing 'wallet' address

    Emits:
        leave_response: Confirmation of room leave
    """
    try:
        if not data or 'wallet' not in data:
            emit('error', {'message': 'wallet address is required'})
            return

        wallet = data['wallet'].strip()

        if not validate_wallet_address(wallet):
            emit('error', {'message': 'Invalid wallet address format'})
            return

        leave_room(wallet)
        logger.info(f"Client {request.sid} left room: {wallet}")

        emit('leave_response', {
            'status': 'left',
            'wallet': wallet,
            'message': f'Left notification room for {wallet}'
        })

    except Exception as e:
        logger.error(f"Error in handle_leave: {e}")
        emit('error', {'message': 'Failed to leave room'})


@socketio.on('ping')
def handle_ping():
    """
    Handle ping (heartbeat) from client.

    Emits:
        pong: Response to ping
    """
    emit('pong', {
        'timestamp': datetime.utcnow().isoformat()
    })


# ===========================
# Helper Functions for External Services
# ===========================

def emit_mining_reward(wallet_address, amount_advc, ap_awarded, pool=None):
    """
    Emit mining reward event to client.

    This function should be called by mining monitoring services
    when a new mining event is detected.

    Args:
        wallet_address: Player wallet address
        amount_advc: Amount of ADVC mined
        ap_awarded: AP awarded for this mining event
        pool: Mining pool name (optional)
    """
    try:
        with app.app_context():
            # Update player stats
            player = Player.query.filter_by(wallet_address=wallet_address).first()
            if player:
                player.total_mined_advc += Decimal(str(amount_advc))
                player.total_ap += ap_awarded

                # Create mining event record
                mining_event = MiningEvent(
                    wallet_address=wallet_address,
                    amount_advc=Decimal(str(amount_advc)),
                    ap_awarded=ap_awarded,
                    pool=pool
                )

                db.session.add(mining_event)
                db.session.commit()

                # Emit WebSocket event
                socketio.emit('mining_reward', {
                    'amount_advc': float(amount_advc),
                    'ap_awarded': ap_awarded,
                    'pool': pool,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=wallet_address)

                logger.info(f"Mining reward emitted: {wallet_address} - {amount_advc} ADVC, {ap_awarded} AP")

    except Exception as e:
        logger.error(f"Error emitting mining reward: {e}")
        db.session.rollback()


def emit_achievement_unlocked(wallet_address, achievement_id):
    """
    Emit achievement unlocked event to client.

    This function should be called when a player unlocks an achievement.

    Args:
        wallet_address: Player wallet address
        achievement_id: ID of unlocked achievement
    """
    try:
        with app.app_context():
            # Check if already unlocked
            existing = PlayerAchievement.query.filter_by(
                wallet_address=wallet_address,
                achievement_id=achievement_id
            ).first()

            if existing:
                logger.warning(f"Achievement {achievement_id} already unlocked for {wallet_address}")
                return

            # Get achievement details
            achievement = Achievement.query.get(achievement_id)
            if not achievement:
                logger.error(f"Achievement {achievement_id} not found")
                return

            # Create player achievement record
            player_achievement = PlayerAchievement(
                wallet_address=wallet_address,
                achievement_id=achievement_id
            )

            # Award AP
            player = Player.query.filter_by(wallet_address=wallet_address).first()
            if player:
                player.total_ap += achievement.ap_reward

            db.session.add(player_achievement)
            db.session.commit()

            # Emit WebSocket event
            socketio.emit('achievement_unlocked', {
                'achievement_id': achievement_id,
                'name': achievement.name,
                'ap_reward': achievement.ap_reward,
                'timestamp': datetime.utcnow().isoformat()
            }, room=wallet_address)

            logger.info(f"Achievement unlocked: {wallet_address} - {achievement.name}")

    except Exception as e:
        logger.error(f"Error emitting achievement unlocked: {e}")
        db.session.rollback()


def emit_rank_changed(wallet_address, new_rank, old_rank):
    """
    Emit rank changed event to client.

    This function should be called when a player's leaderboard rank changes.

    Args:
        wallet_address: Player wallet address
        new_rank: New rank position
        old_rank: Previous rank position
    """
    try:
        socketio.emit('rank_changed', {
            'new_rank': new_rank,
            'old_rank': old_rank,
            'timestamp': datetime.utcnow().isoformat()
        }, room=wallet_address)

        logger.info(f"Rank changed: {wallet_address} - {old_rank} -> {new_rank}")

    except Exception as e:
        logger.error(f"Error emitting rank changed: {e}")


# ===========================
# Application Entry Point
# ===========================

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'

    logger.info(f"Starting M2P Flask server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    # Start verification monitor
    logger.info("Starting verification monitor...")
    verification_monitor.start()

    # Run with SocketIO
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
