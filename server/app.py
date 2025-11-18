"""
M2P (Mine to Play) - Flask application with WebSocket support
Main server application with achievement system integration
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging
import asyncio
from typing import Dict, List

from server.models import Base, Player, Achievement
from server.achievements import AchievementManager
from server.pool_poller import PoolPoller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Database setup
DATABASE_URL = 'sqlite:///./m2p.db'
engine = create_engine(DATABASE_URL, echo=False)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Create tables
Base.metadata.create_all(engine)

# WebSocket connection tracking
active_connections: Dict[int, str] = {}  # player_id -> session_id


# ===== DATABASE CONTEXT MANAGER =====

@contextmanager
def get_db():
    """Database session context manager"""
    db = Session()
    try:
        yield db
    finally:
        db.close()


# ===== WEBSOCKET MANAGER =====

class WebSocketManager:
    """Manages WebSocket connections and notifications"""

    @staticmethod
    async def send_to_user(player_id: int, message: Dict):
        """Send a message to a specific user"""
        session_id = active_connections.get(player_id)
        if session_id:
            socketio.emit('notification', message, room=session_id)
            logger.debug(f"Sent notification to player {player_id}: {message['type']}")

    @staticmethod
    def broadcast(message: Dict):
        """Broadcast a message to all connected users"""
        socketio.emit('broadcast', message)


ws_manager = WebSocketManager()


# ===== WEBSOCKET EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to M2P server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    # Remove from active connections
    for player_id, sid in list(active_connections.items()):
        if sid == request.sid:
            del active_connections[player_id]
            logger.info(f"Player {player_id} disconnected")
            break


@socketio.on('authenticate')
def handle_authenticate(data):
    """Authenticate a user and join their personal room"""
    player_id = data.get('player_id')
    if player_id:
        active_connections[player_id] = request.sid
        join_room(request.sid)
        logger.info(f"Player {player_id} authenticated with session {request.sid}")
        emit('authenticated', {'player_id': player_id, 'status': 'success'})


# ===== API ENDPOINTS =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'M2P'})


@app.route('/api/players', methods=['POST'])
def create_player():
    """Create a new player"""
    data = request.json

    with get_db() as db:
        # Check if player already exists
        existing = db.query(Player).filter(
            (Player.username == data['username']) |
            (Player.wallet_address == data['wallet_address'])
        ).first()

        if existing:
            return jsonify({'error': 'Player already exists'}), 400

        # Create new player
        player = Player(
            username=data['username'],
            email=data.get('email'),
            wallet_address=data['wallet_address'],
            unique_pools_mined=[]
        )
        db.add(player)
        db.commit()
        db.refresh(player)

        return jsonify({
            'id': player.id,
            'username': player.username,
            'wallet_address': player.wallet_address,
            'total_mined': player.total_mined,
            'total_ap': player.total_ap
        }), 201


@app.route('/api/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """Get player information"""
    with get_db() as db:
        player = db.query(Player).filter(Player.id == player_id).first()

        if not player:
            return jsonify({'error': 'Player not found'}), 404

        return jsonify({
            'id': player.id,
            'username': player.username,
            'wallet_address': player.wallet_address,
            'total_mined': player.total_mined,
            'total_ap': player.total_ap,
            'consecutive_days': player.consecutive_mining_days,
            'total_mining_events': player.total_mining_events,
            'unique_pools_count': len(player.unique_pools_mined or []),
            'last_mining_date': player.last_mining_date.isoformat() if player.last_mining_date else None
        })


@app.route('/api/players/<int:player_id>/achievements', methods=['GET'])
def get_player_achievements(player_id):
    """Get all achievements for a player with progress"""
    with get_db() as db:
        player = db.query(Player).filter(Player.id == player_id).first()

        if not player:
            return jsonify({'error': 'Player not found'}), 404

        achievement_manager = AchievementManager(db)
        achievements = achievement_manager.get_player_achievements(player)
        stats = achievement_manager.get_achievement_stats(player)

        return jsonify({
            'achievements': achievements,
            'stats': stats
        })


@app.route('/api/players/<int:player_id>/achievements/check', methods=['POST'])
def check_player_achievements(player_id):
    """Manually trigger achievement check for a player"""
    with get_db() as db:
        player = db.query(Player).filter(Player.id == player_id).first()

        if not player:
            return jsonify({'error': 'Player not found'}), 404

        achievement_manager = AchievementManager(db)
        newly_unlocked = achievement_manager.check_achievements(player)

        return jsonify({
            'newly_unlocked': newly_unlocked,
            'count': len(newly_unlocked)
        })


@app.route('/api/achievements', methods=['GET'])
def get_all_achievements():
    """Get all achievements (for display purposes)"""
    with get_db() as db:
        achievements = db.query(Achievement).filter(
            Achievement.is_hidden == False
        ).order_by(Achievement.category, Achievement.sort_order).all()

        return jsonify([
            {
                'id': a.achievement_id,
                'name': a.name,
                'description': a.description,
                'icon': a.icon,
                'ap_reward': a.ap_reward,
                'category': a.category,
                'condition_type': a.condition_type,
                'condition_value': a.condition_value
            }
            for a in achievements
        ])


@app.route('/api/mining/reward', methods=['POST'])
def process_mining_reward():
    """
    Process a mining reward for a player.
    This endpoint is called when a player earns mining rewards.
    """
    data = request.json

    required_fields = ['player_id', 'amount', 'pool_id', 'pool_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    with get_db() as db:
        poller = PoolPoller(db, ws_manager)

        try:
            # Process the reward (runs async code in sync context)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                poller.process_mining_reward(
                    player_id=data['player_id'],
                    amount=data['amount'],
                    pool_id=data['pool_id'],
                    pool_name=data['pool_name']
                )
            )
            loop.close()

            return jsonify(result), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error processing mining reward: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/players/<int:player_id>/mining-stats', methods=['GET'])
def get_mining_stats(player_id):
    """Get detailed mining statistics for a player"""
    with get_db() as db:
        poller = PoolPoller(db)
        stats = poller.get_player_mining_stats(player_id)

        if not stats:
            return jsonify({'error': 'Player not found'}), 404

        return jsonify(stats)


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard rankings"""
    category = request.args.get('category', 'total_mined')
    limit = min(int(request.args.get('limit', 100)), 100)

    with get_db() as db:
        # Query based on category
        if category == 'total_mined':
            query = db.query(Player).order_by(Player.total_mined.desc())
        elif category == 'total_ap':
            query = db.query(Player).order_by(Player.total_ap.desc())
        elif category == 'consecutive_days':
            query = db.query(Player).order_by(Player.consecutive_mining_days.desc())
        else:
            return jsonify({'error': 'Invalid category'}), 400

        players = query.limit(limit).all()

        return jsonify([
            {
                'rank': idx + 1,
                'player_id': p.id,
                'username': p.username,
                'value': getattr(p, category),
                'total_ap': p.total_ap
            }
            for idx, p in enumerate(players)
        ])


@app.route('/api/admin/award-achievement', methods=['POST'])
def award_special_achievement():
    """Manually award a special achievement (admin endpoint)"""
    data = request.json

    with get_db() as db:
        player = db.query(Player).filter(Player.id == data['player_id']).first()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        achievement_manager = AchievementManager(db)
        result = achievement_manager.award_special_achievement(
            player,
            data['achievement_id']
        )

        if result:
            # Send WebSocket notification
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ws_manager.send_to_user(player.id, {
                    'type': 'achievement_unlocked',
                    'achievement': result
                })
            )
            loop.close()

            return jsonify(result), 200
        else:
            return jsonify({'error': 'Achievement already unlocked or not found'}), 400


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ===== MAIN ENTRY POINT =====

if __name__ == '__main__':
    logger.info("Starting M2P server...")
    logger.info(f"Database: {DATABASE_URL}")

    # Run the server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
