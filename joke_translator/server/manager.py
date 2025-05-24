"""
Connection manager for WebSocket connections and statistics tracking.
"""

import asyncio
import time
from typing import Dict, Set
from fastapi import WebSocket

class ConnectionManager:
    """Manages WebSocket connections and tracks statistics."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_stats: Dict[WebSocket, dict] = {}
        self.dashboard_connections: Set[WebSocket] = set()
        # Track pending translations with their start times
        self.pending_translations: Dict[int, float] = {}  # joke_id -> start_time
        # Global statistics that persist across client disconnections
        self.global_stats = {
            "total_jokes_sent": 0,
            "total_translations": 0,
            "translation_history": [],  # List of (timestamp, duration) tuples
            "session_start_time": None,
            "total_clients_served": 0
        }
    
    async def connect(self, websocket: WebSocket):
        """Connect a new client WebSocket."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_stats[websocket] = {
            "jokes_sent": 0,
            "translations_received": 0,
            "translation_times": []
        }
        self.global_stats["total_clients_served"] += 1
        if self.global_stats["session_start_time"] is None:
            self.global_stats["session_start_time"] = time.time()
        await self.broadcast_stats()
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Connect a new dashboard WebSocket."""
        await websocket.accept()
        self.dashboard_connections.add(websocket)
        await self.send_stats_to_dashboard(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket and clean up its resources."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_stats:
                del self.connection_stats[websocket]
            await self.broadcast_stats()
        elif websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)
    
    async def send_joke(self, websocket: WebSocket, joke_id: int, joke: str):
        """Send a joke to a client and start tracking its translation time."""
        message = {"id": joke_id, "joke": joke}
        await websocket.send_json(message)
        self.connection_stats[websocket]["jokes_sent"] += 1
        self.global_stats["total_jokes_sent"] += 1
        self.pending_translations[joke_id] = time.time()
        await self.broadcast_stats()
    
    def record_translation(self, websocket: WebSocket, joke_id: int):
        """Record the translation time for a joke."""
        if joke_id in self.pending_translations:
            translation_time = time.time() - self.pending_translations[joke_id]
            translation_time = round(translation_time, 2)  # Round to 2 decimal places
            
            stats = self.connection_stats[websocket]
            stats["translations_received"] += 1
            stats["translation_times"].append(translation_time)
            
            # Update global statistics
            self.global_stats["total_translations"] += 1
            self.global_stats["translation_history"].append((time.time(), translation_time))
            
            # Keep only the last 100 translations in history to manage memory
            if len(self.global_stats["translation_history"]) > 100:
                self.global_stats["translation_history"] = self.global_stats["translation_history"][-100:]
            
            del self.pending_translations[joke_id]
            asyncio.create_task(self.broadcast_stats())
    
    async def broadcast_stats(self):
        """Broadcast current statistics to all dashboard connections."""
        if not self.dashboard_connections:
            return
            
        current_time = time.time()
        session_duration = (
            current_time - self.global_stats["session_start_time"]
            if self.global_stats["session_start_time"] is not None
            else 0
        )

        recent_translations = self.global_stats["translation_history"][-15:]
        translation_times = [t[1] for t in recent_translations]
        translation_timestamps = [t[0] for t in recent_translations]
            
        stats_data = {
            "type": "stats_update",
            "clients": {
                str(id(ws)): stats for ws, stats in self.connection_stats.items()
            },
            "global_stats": {
                "total_jokes_sent": self.global_stats["total_jokes_sent"],
                "total_translations": self.global_stats["total_translations"],
                "avg_translation_time": (
                    round(sum(t[1] for t in self.global_stats["translation_history"]) / len(self.global_stats["translation_history"]), 2)
                    if self.global_stats["translation_history"]
                    else 0
                ),
                "recent_translations": {
                    "times": translation_times,
                    "timestamps": translation_timestamps
                },
                "total_clients_served": self.global_stats["total_clients_served"],
                "session_duration": session_duration,
                "active_clients": len(self.active_connections)
            }
        }
        
        for ws in self.dashboard_connections:
            try:
                await ws.send_json(stats_data)
            except:
                pass
    
    async def send_stats_to_dashboard(self, websocket: WebSocket):
        """Send current statistics to a specific dashboard connection."""
        await self.broadcast_stats()

    def get_client_translations(self, websocket: WebSocket) -> int:
        """Get the number of translations completed by a client."""
        if websocket in self.connection_stats:
            return self.connection_stats[websocket]["translations_received"]
        return 0 