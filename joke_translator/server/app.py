"""
FastAPI application module for the Joke Translator server.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from joke_translator.server.manager import ConnectionManager
from joke_translator.utils.joke_generator import JokeGenerator

# Initialize FastAPI app
app = FastAPI(title="Joke Translator")

# Set up static files and templates
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize managers
connection_manager = ConnectionManager()
joke_generator = JokeGenerator()

async def send_jokes(websocket: WebSocket):
    """Send jokes to the client every 200ms."""
    try:
        while True:
            # Check if client has completed 5 translations
            if connection_manager.get_client_translations(websocket) >= 5:
                break
                
            joke_id, joke = joke_generator.get_joke()
            await connection_manager.send_joke(websocket, joke_id, joke)
            await asyncio.sleep(0.2)  # 200ms delay
    except Exception as e:
        print(f"Error sending jokes: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle client WebSocket connections."""
    await connection_manager.connect(websocket)
    try:
        # Start sending jokes asynchronously
        joke_task = asyncio.create_task(send_jokes(websocket))
        
        # Handle translation completion messages
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "translation_complete":
                joke_id = data.get("id")
                if joke_id is not None:
                    connection_manager.record_translation(websocket, joke_id)
                    # Check if client has completed 5 translations
                    if connection_manager.get_client_translations(websocket) >= 5:
                        break
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
    finally:
        # Clean up tasks and disconnect
        if 'joke_task' in locals():
            joke_task.cancel()
        await connection_manager.disconnect(websocket)

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """Handle dashboard WebSocket connections."""
    await connection_manager.connect_dashboard(websocket)
    try:
        await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    ) 