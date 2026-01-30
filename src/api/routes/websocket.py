"""
WebSocket hub for real-time model list synchronization
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
import json

from api.services.model_store import (
    get_all_models,
    add_official_model_async,
    add_custom_model_async,
    subscribe_async,
    unsubscribe,
)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept and register a new connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)

        # Send initial model list
        models = get_all_models()
        await self._send_message(websocket, {
            "type": "init",
            "data": models
        })

    async def disconnect(self, websocket: WebSocket):
        """Remove a connection"""
        async with self._lock:
            self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        async with self._lock:
            connections = list(self.active_connections)

        disconnected = []
        for connection in connections:
            try:
                await self._send_message(connection, message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for conn in disconnected:
                    self.active_connections.discard(conn)

    async def _send_message(self, websocket: WebSocket, message: dict):
        """Send a message to a single client"""
        await websocket.send_json(message)

    async def handle_model_update(self, store: dict, version: int):
        """Handle model store updates - broadcast to all clients"""
        await self.broadcast({
            "type": "model_added",
            "data": {
                "official": store.get("official", []),
                "custom": store.get("custom", []),
                "version": version
            }
        })


# Global connection manager
manager = ConnectionManager()

# Subscribe to model store changes
subscribe_async(manager.handle_model_update)


@router.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time model list synchronization.

    Protocol:
    - Server sends 'init' message on connection with current model list
    - Server sends 'model_added' message when model list changes
    - Client can send 'add_model' message to add a new model

    Message format:
    {
        "type": "init" | "model_added" | "add_model" | "error",
        "data": { "official": [...], "custom": [...], "version": int },
        "name": "model-name",  // for add_model
        "category": "official" | "custom",  // for add_model
        "error": "error message"  // for error type
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "add_model":
                name = data.get("name", "").strip()
                category = data.get("category", "custom")

                if not name or len(name) < 2:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Invalid model name"
                    })
                    continue

                try:
                    if category == "official":
                        await add_official_model_async(name)
                    else:
                        await add_custom_model_async(name)

                    # Model added - broadcast will be triggered by subscriber
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e)
                    })

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)
