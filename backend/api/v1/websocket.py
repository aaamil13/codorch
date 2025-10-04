"""
WebSocket endpoints for real-time updates.

Provides:
- Real-time module change notifications
- Real-time alerts
- Real-time monitoring events
"""

from typing import Any, Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from uuid import UUID
import asyncio
import json

from backend.core.event_emitter import get_event_emitter

router = APIRouter(prefix="/ws", tags=["websocket"])

# Active WebSocket connections per project
active_connections: Dict[str, List[WebSocket]] = {}


@router.websocket("/project/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str) -> None:
    """
    WebSocket endpoint for real-time project updates.

    Broadcasts:
    - Module changes
    - Dependency changes
    - Alerts from monitoring
    - Rule violations
    """
    await websocket.accept()

    # Add to active connections
    if project_id not in active_connections:
        active_connections[project_id] = []
    active_connections[project_id].append(websocket)

    event_emitter = get_event_emitter()

    # Register event listeners
    def send_module_change(data: Dict[str, Any]) -> None:
        """Send module change event to this WebSocket."""
        if data.get("project_id") == project_id:
            asyncio.create_task(safe_send(websocket, {"type": "module_changed", "data": data}))

    def send_alert(data: Dict[str, Any]) -> None:
        """Send alert event to this WebSocket."""
        if data.get("project_id") == project_id:
            asyncio.create_task(safe_send(websocket, {"type": "alert", "data": data}))

    def send_dependency_change(data: Dict[str, Any]) -> None:
        """Send dependency change event."""
        if data.get("project_id") == project_id:
            asyncio.create_task(safe_send(websocket, {"type": "dependency_changed", "data": data}))

    # Subscribe to events
    event_emitter.on("module_changed", send_module_change)
    event_emitter.on("alert", send_alert)
    event_emitter.on("dependency_changed", send_dependency_change)

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive ping/commands from client
            data = await websocket.receive_text()

            # Handle client commands if needed
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        # Client disconnected
        print(f"WebSocket disconnected for project {project_id}")

    finally:
        # Cleanup
        if project_id in active_connections:
            active_connections[project_id].remove(websocket)
            if not active_connections[project_id]:
                del active_connections[project_id]

        # Unsubscribe from events
        event_emitter.off("module_changed", send_module_change)
        event_emitter.off("alert", send_alert)
        event_emitter.off("dependency_changed", send_dependency_change)


async def safe_send(websocket: WebSocket, message: dict) -> None:
    """Safely send message to WebSocket."""
    try:
        await websocket.send_json(message)
    except Exception as e:
        print(f"Failed to send WebSocket message: {e}")


async def broadcast_to_project(project_id: str, message: dict) -> None:
    """
    Broadcast message to all WebSocket clients for project.

    Usage:
        await broadcast_to_project(
            project_id,
            {"type": "alert", "data": {...}}
        )
    """
    if project_id in active_connections:
        disconnected = []

        for connection in active_connections[project_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        # Remove disconnected
        for conn in disconnected:
            active_connections[project_id].remove(conn)
