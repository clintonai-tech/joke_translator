#!/usr/bin/env python3
"""
Script to run the Joke Translator client with command line options.
"""

import argparse
from dotenv import load_dotenv
from joke_translator.client.websocket_client import JokeTranslatorClient

def on_joke(joke_id: int, joke: str):
    """Callback for when a joke is received."""
    print(f"\nReceived joke #{joke_id}:")
    print(f"Original: {joke}")

def on_translation(translation: str):
    """Callback for when a translation is received."""
    print(f"Translation: {translation}")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a Joke Translator client")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--target-lang",
        default="de",
        help="Target language code (default: de)"
    )
    parser.add_argument(
        "--gpt",
        action="store_true",
        help="Use GPT-4 for translations (default: use DeepL)"
    )
    
    args = parser.parse_args()
    
    # Create and run the client
    client = JokeTranslatorClient(
        uri=f"ws://{args.host}:{args.port}/ws"
    )
    
    # Determine translation service
    translation_service = "gpt" if args.gpt else "deepl"
    
    print(f"Connecting to server at ws://{args.host}:{args.port}/ws")
    print(f"Target language: {args.target_lang}")
    print(f"Translation service: {translation_service}")
    print("\nPress Ctrl+C to exit\n")
    
    try:
        client.start(target_lang=args.target_lang, translation_service=translation_service)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main() 