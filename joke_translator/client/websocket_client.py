"""
Simple WebSocket client for translating jokes.
"""

import asyncio
import json
import sys
import websockets
from typing import Dict
from .translator import TranslatorService

class JokeTranslatorClient:
    def __init__(self, uri: str = "ws://localhost:8000/ws"):
        self.uri = uri
        self.translator = TranslatorService()
        self.translations_completed = 0
        self.max_translations = 5
        self.active_translations: Dict[int, asyncio.Task] = {}

    async def translate_and_send(self, websocket, joke_id: int, joke_text: str, target_lang: str, translation_service: str):
        """Translate a joke and send it back to the server."""
        try:
            # Translate the joke
            translated_text = await self.translator.translate(joke_text, target_lang, translation_service)
            if translated_text:
                # Send translation back to server
                response = {
                    "type": "translation_complete",
                    "id": joke_id,
                    "translated_joke": translated_text
                }
                await websocket.send(json.dumps(response))
                
                # Update counter and cleanup
                self.translations_completed += 1
                print(f"Translation {self.translations_completed}/{self.max_translations} completed")
                
                # Exit if we've completed all translations
                if self.translations_completed >= self.max_translations:
                    print("\nCompleted all translations. Disconnecting...")
                    await websocket.close()
                    sys.exit(0)
                    
        except Exception as e:
            print(f"Error translating joke {joke_id}: {e}")
        finally:
            # Clean up the active translation
            if joke_id in self.active_translations:
                del self.active_translations[joke_id]

    async def run(self, target_lang: str = "de", translation_service: str = "deepl"):
        """Run the client until max translations are reached."""
        try:
            async with websockets.connect(self.uri) as websocket:
                print(f"Connected to server at {self.uri}")
                
                while self.translations_completed < self.max_translations:
                    try:
                        # Receive joke from server
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if "joke" in data:
                            joke_id = data["id"]
                            joke_text = data["joke"]
                            
                            # Start translation task if we haven't reached the limit
                            if self.translations_completed < self.max_translations:
                                print(f"\nReceived joke #{joke_id}: {joke_text}")
                                
                                # Create and track translation task
                                task = asyncio.create_task(
                                    self.translate_and_send(websocket, joke_id, joke_text, target_lang, translation_service)
                                )
                                self.active_translations[joke_id] = task
                                
                                # Clean up completed tasks
                                done_tasks = [
                                    task_id for task_id, task in self.active_translations.items()
                                    if task.done()
                                ]
                                for task_id in done_tasks:
                                    del self.active_translations[task_id]
                    
                    except websockets.exceptions.ConnectionClosed:
                        print("Server closed the connection")
                        break
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        break
                
                # Wait for any remaining translations to complete
                if self.active_translations:
                    print("Waiting for pending translations to complete...")
                    await asyncio.gather(*self.active_translations.values(), return_exceptions=True)
                    
                # Exit after completing all translations
                if self.translations_completed >= self.max_translations:
                    print("\nCompleted all translations. Disconnecting...")
                    sys.exit(0)
                
        except Exception as e:
            print(f"Connection error: {e}")

    def start(self, target_lang: str = "de", translation_service: str = "deepl"):
        """Start the client in the current event loop."""
        try:
            asyncio.get_event_loop().run_until_complete(self.run(target_lang, translation_service))
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            # Ensure we exit after completion
            if self.translations_completed >= self.max_translations:
                sys.exit(0) 