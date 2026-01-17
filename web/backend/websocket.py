"""WebSocket handler for real-time state updates."""

import asyncio
from fastapi import WebSocket, WebSocketDisconnect

from .services.device_manager import device_manager


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._broadcast_queue: asyncio.Queue = asyncio.Queue()
        self._broadcast_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

        # Register for state updates from device manager
        device_manager.add_state_callback(self._on_state_update)

        # Start broadcast task if not running
        if self._broadcast_task is None or self._broadcast_task.done():
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

        # Send initial state
        state = await device_manager.get_state()
        await websocket.send_json({
            "type": "connection",
            "payload": {
                "connected": device_manager.is_connected,
                "device_name": device_manager.device_name,
                "device_address": device_manager.device_address,
            },
        })
        if device_manager.is_connected:
            await websocket.send_json({
                "type": "state",
                "payload": state,
            })

    def disconnect(self, websocket: WebSocket) -> None:
        """Handle WebSocket disconnection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Remove callback if no more connections
        if not self.active_connections:
            device_manager.remove_state_callback(self._on_state_update)
            if self._broadcast_task:
                self._broadcast_task.cancel()
                self._broadcast_task = None

    async def _on_state_update(self, message: dict) -> None:
        """Callback for device manager state updates."""
        await self._broadcast_queue.put(message)

    async def _broadcast_loop(self) -> None:
        """Process broadcast queue and send to all clients."""
        while True:
            try:
                message = await self._broadcast_queue.get()
                await self._broadcast(message)
            except asyncio.CancelledError:
                break
            except Exception:
                continue

    async def _broadcast(self, message: dict) -> None:
        """Send message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def handle_message(self, websocket: WebSocket, data: dict) -> None:
        """Handle incoming WebSocket message."""
        msg_type = data.get("type")

        if msg_type == "refresh":
            # Request immediate state refresh
            if device_manager.is_connected:
                state = await device_manager.get_state()
                await websocket.send_json({
                    "type": "state",
                    "payload": state,
                })


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint handler."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
