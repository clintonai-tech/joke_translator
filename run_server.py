#!/usr/bin/env python3
"""
Script to run the Joke Translator server with command line options.
"""

import argparse
import uvicorn
from dotenv import load_dotenv
import os

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Joke Translator server")
    parser.add_argument(
        "--gpt",
        action="store_true",
        help="Use GPT-4 to generate jokes"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    
    args = parser.parse_args()
    
    # Set environment variable for joke generation mode
    if args.gpt:
        os.environ["USE_GPT4_JOKES"] = "1"
    
    # Run the server
    uvicorn.run(
        "joke_translator.server.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main() 