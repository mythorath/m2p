"""WebSocket server for real-time updates."""
import json
import logging
from typing import Set, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, wallet_address: str = None):
        """Connect a new WebSocket client.

        Args:
            websocket: WebSocket connection
            wallet_address: Optional wallet address for user-specific notifications
        """
        await websocket.accept()
        self.active_connections.add(websocket)

        if wallet_address:
            if wallet_address not in self.user_connections:
                self.user_connections[wallet_address] = set()
            self.user_connections[wallet_address].add(websocket)

        logger.info(f"WebSocket connected (total: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket, wallet_address: str = None):
        """Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection
            wallet_address: Optional wallet address
        """
        self.active_connections.discard(websocket)

        if wallet_address and wallet_address in self.user_connections:
            self.user_connections[wallet_address].discard(websocket)
            if not self.user_connections[wallet_address]:
                del self.user_connections[wallet_address]

        logger.info(f"WebSocket disconnected (total: {len(self.active_connections)})")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to a specific connection.

        Args:
            message: Message to send
            websocket: WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections.

        Args:
            message: Message to broadcast
        """
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.active_connections.discard(connection)

    async def send_to_user(self, wallet_address: str, message: Dict[str, Any]):
        """Send message to all connections for a specific user.

        Args:
            wallet_address: User's wallet address
            message: Message to send
        """
        if wallet_address not in self.user_connections:
            return

        disconnected = set()

        for connection in self.user_connections[wallet_address]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {wallet_address}: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.user_connections[wallet_address].discard(connection)

    async def emit_rank_changed(
        self,
        wallet_address: str,
        period: str,
        old_rank: int,
        new_rank: int,
        period_score: float
    ):
        """Emit rank change event.

        Args:
            wallet_address: User's wallet address
            period: Leaderboard period
            old_rank: Previous rank
            new_rank: New rank
            period_score: Current period score
        """
        rank_change = new_rank - old_rank

        message = {
            "event": "rank_changed",
            "data": {
                "wallet_address": wallet_address,
                "period": period,
                "old_rank": old_rank,
                "new_rank": new_rank,
                "rank_change": rank_change,
                "direction": "up" if rank_change < 0 else "down" if rank_change > 0 else "same",
                "period_score": period_score,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

        # Send to specific user
        await self.send_to_user(wallet_address, message)

        # Broadcast to all (for leaderboard updates)
        await self.broadcast({
            "event": "leaderboard_updated",
            "data": {
                "period": period,
                "timestamp": datetime.utcnow().isoformat(),
            }
        })

    async def emit_leaderboard_updated(self, period: str):
        """Emit leaderboard update event.

        Args:
            period: Leaderboard period that was updated
        """
        message = {
            "event": "leaderboard_updated",
            "data": {
                "period": period,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

        await self.broadcast(message)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, wallet_address: str = None):
    """WebSocket endpoint handler.

    Args:
        websocket: WebSocket connection
        wallet_address: Optional wallet address for user-specific notifications
    """
    await manager.connect(websocket, wallet_address)

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()

            # Echo back for now (can implement more complex handlers)
            try:
                message = json.loads(data)
                await manager.send_personal_message({
                    "event": "echo",
                    "data": message
                }, websocket)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "event": "error",
                    "data": {"message": "Invalid JSON"}
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, wallet_address)
