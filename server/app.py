"""
M2P Flask Application with WebSocket Support
Handles player registration, verification, and admin endpoints
"""
import os
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import random

from server.models import Base, Player, VerificationLog
from server.config import DATABASE_URL, ADMIN_API_KEY, SOCKETIO_ASYNC_MODE
from server.verifier import WalletVerifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production')
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=SOCKETIO_ASYNC_MODE)

# Initialize database
engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))

# Initialize wallet verifier
verifier = None


def get_verifier():
    """Get or create wallet verifier instance"""
    global verifier
    if verifier is None:
        db_session = Session()
        verifier = WalletVerifier(db_session, socketio)
        verifier.start_verification_loop()
    return verifier


def require_admin_auth(func):
    """Decorator to require admin authentication"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        api_key = request.headers.get('X-API-Key')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if token == ADMIN_API_KEY:
                return func(*args, **kwargs)

        if api_key and api_key == ADMIN_API_KEY:
            return func(*args, **kwargs)

        return jsonify({'error': 'Unauthorized'}), 401

    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'M2P Wallet Verification',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/register', methods=['POST'])
def register_player():
    """
    Register a new player for verification

    Request body:
    {
        "wallet_address": "string"
    }

    Response:
    {
        "success": true,
        "player": {...},
        "verification_amount": float,
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address', '').strip()

        if not wallet_address:
            return jsonify({'error': 'Wallet address is required'}), 400

        db = Session()

        # Check if player already exists
        existing_player = db.query(Player).filter_by(wallet_address=wallet_address).first()

        if existing_player:
            if existing_player.verified:
                return jsonify({
                    'success': False,
                    'message': 'Wallet already verified',
                    'player': existing_player.to_dict()
                }), 200
            else:
                # Return existing verification challenge
                return jsonify({
                    'success': True,
                    'player': existing_player.to_dict(),
                    'verification_amount': existing_player.verification_amount,
                    'message': 'Verification challenge already active'
                }), 200

        # Generate random verification amount (between 0.1 and 1.0 ADVC)
        verification_amount = round(random.uniform(0.1, 1.0), 4)

        # Create new player
        new_player = Player(
            wallet_address=wallet_address,
            verification_amount=verification_amount,
            verification_requested_at=datetime.utcnow()
        )

        db.add(new_player)
        db.commit()
        db.refresh(new_player)

        logger.info(f"New player registered: {wallet_address} with amount {verification_amount}")

        return jsonify({
            'success': True,
            'player': new_player.to_dict(),
            'verification_amount': verification_amount,
            'message': f'Please send exactly {verification_amount} ADVC to the dev wallet to verify'
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        db.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@app.route('/api/player/<wallet_address>', methods=['GET'])
def get_player(wallet_address):
    """
    Get player information

    Response:
    {
        "success": true,
        "player": {...}
    }
    """
    try:
        db = Session()
        player = db.query(Player).filter_by(wallet_address=wallet_address).first()

        if not player:
            return jsonify({'error': 'Player not found'}), 404

        return jsonify({
            'success': True,
            'player': player.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Get player error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@app.route('/api/verify-now', methods=['POST'])
def verify_now():
    """
    Manually trigger verification check for a player

    Request body:
    {
        "wallet_address": "string"
    }

    Response:
    {
        "success": true,
        "verified": bool,
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address', '').strip()

        if not wallet_address:
            return jsonify({'error': 'Wallet address is required'}), 400

        db = Session()
        player = db.query(Player).filter_by(wallet_address=wallet_address).first()

        if not player:
            return jsonify({'error': 'Player not found'}), 404

        if player.verified:
            return jsonify({
                'success': True,
                'verified': True,
                'message': 'Player already verified'
            }), 200

        # Get verifier and attempt verification
        wallet_verifier = get_verifier()
        wallet_verifier.db = db
        verified = wallet_verifier.verify_donation(player)

        if verified:
            db.refresh(player)
            return jsonify({
                'success': True,
                'verified': True,
                'player': player.to_dict(),
                'message': 'Verification successful!'
            }), 200
        else:
            return jsonify({
                'success': True,
                'verified': False,
                'message': 'Verification pending. Transaction not found yet.'
            }), 200

    except Exception as e:
        logger.error(f"Verify now error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@app.route('/admin/verify-player', methods=['POST'])
@require_admin_auth
def admin_verify_player():
    """
    Manually verify a player (admin only)

    Request body:
    {
        "wallet_address": "string",
        "tx_hash": "string" (optional)
    }

    Headers:
    Authorization: Bearer <admin_api_key>
    OR
    X-API-Key: <admin_api_key>

    Response:
    {
        "success": true,
        "player": {...},
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address', '').strip()
        tx_hash = data.get('tx_hash', 'manual_verification').strip()

        if not wallet_address:
            return jsonify({'error': 'Wallet address is required'}), 400

        db = Session()
        player = db.query(Player).filter_by(wallet_address=wallet_address).first()

        if not player:
            return jsonify({'error': 'Player not found'}), 404

        if player.verified:
            return jsonify({
                'success': False,
                'message': 'Player already verified',
                'player': player.to_dict()
            }), 200

        # Manually verify the player
        wallet_verifier = get_verifier()
        wallet_verifier.db = db
        wallet_verifier.mark_verified(player, tx_hash, method='manual_admin')

        db.refresh(player)

        logger.info(f"Admin manually verified player: {wallet_address}")

        return jsonify({
            'success': True,
            'player': player.to_dict(),
            'message': 'Player manually verified successfully'
        }), 200

    except Exception as e:
        logger.error(f"Admin verify error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@app.route('/admin/players', methods=['GET'])
@require_admin_auth
def admin_get_players():
    """
    Get all players (admin only)

    Query parameters:
    - verified: Filter by verification status (true/false)
    - limit: Number of results (default: 100)
    - offset: Pagination offset (default: 0)

    Response:
    {
        "success": true,
        "players": [...],
        "total": int
    }
    """
    try:
        verified_filter = request.args.get('verified')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        db = Session()
        query = db.query(Player)

        if verified_filter is not None:
            verified_bool = verified_filter.lower() == 'true'
            query = query.filter_by(verified=verified_bool)

        total = query.count()
        players = query.order_by(Player.created_at.desc()).limit(limit).offset(offset).all()

        return jsonify({
            'success': True,
            'players': [p.to_dict() for p in players],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"Admin get players error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


@app.route('/admin/verification-logs', methods=['GET'])
@require_admin_auth
def admin_get_verification_logs():
    """
    Get verification logs (admin only)

    Query parameters:
    - wallet_address: Filter by wallet address
    - status: Filter by status
    - limit: Number of results (default: 100)
    - offset: Pagination offset (default: 0)

    Response:
    {
        "success": true,
        "logs": [...],
        "total": int
    }
    """
    try:
        wallet_address = request.args.get('wallet_address')
        status_filter = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        db = Session()
        query = db.query(VerificationLog)

        if wallet_address:
            query = query.filter_by(wallet_address=wallet_address)

        if status_filter:
            query = query.filter_by(status=status_filter)

        total = query.count()
        logs = query.order_by(VerificationLog.created_at.desc()).limit(limit).offset(offset).all()

        log_data = []
        for log in logs:
            log_data.append({
                'id': log.id,
                'player_id': log.player_id,
                'wallet_address': log.wallet_address,
                'verification_method': log.verification_method,
                'status': log.status,
                'tx_hash': log.tx_hash,
                'amount': log.amount,
                'ap_credited': log.ap_credited,
                'error_message': log.error_message,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })

        return jsonify({
            'success': True,
            'logs': log_data,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"Admin get logs error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        db.close()


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to M2P verification service'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join')
def handle_join(data):
    """Join a room (wallet address) for notifications"""
    wallet_address = data.get('wallet_address')
    if wallet_address:
        join_room(wallet_address)
        logger.info(f"Client {request.sid} joined room: {wallet_address}")
        emit('joined', {'wallet_address': wallet_address})


if __name__ == '__main__':
    # Initialize verifier on startup
    get_verifier()

    # Run the app
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting M2P server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
