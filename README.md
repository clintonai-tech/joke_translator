# Joke Translator

A WebSocket-based application that generates jokes and translates them into different languages using either DeepL or GPT-4.

## Features

- WebSocket-based real-time communication
- Support for both DeepL and GPT-4 translation services
- Automatic disconnection after 5 translations
- Concurrent translation handling
- Two joke generation modes:
  - Default: Uses static jokes from jokes.json
  - GPT-4: Generates 50 unique jokes at server startup

## Prerequisites

- Python 3.8+
- OpenAI API key (for GPT-4 features)
- DeepL API key (for DeepL translations)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/clintonai-tech/joke_translator.git
cd joke_translator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
DEEPL_API_KEY=your_deepl_api_key
```

## Usage

### Starting the Server

Run the server with default static jokes:
```bash
python run_server.py
```

Run the server with GPT-4 generated jokes:
```bash
python run_server.py --gpt
```

Server options:
- `--gpt`: Use GPT-4 to generate jokes at startup
- `--host`: Host to bind the server to (default: 127.0.0.1)
- `--port`: Port to bind the server to (default: 8000)
- `--reload`: Enable auto-reload on code changes

### Running the Client

Run the client with DeepL translation (default):
```bash
python run_client.py --target-lang de
```

Run the client with GPT-4 translation:
```bash
python run_client.py --target-lang de --gpt
```

Client options:
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 8000)
- `--target-lang`: Target language code (default: de)
- `--gpt`: Use GPT-4 for translations (default: uses DeepL)

## Architecture

The application consists of:
- Server: FastAPI-based WebSocket server
- Client: Asyncio WebSocket client
- Joke Generator: Manages joke generation and storage
- Translation Services: Integrates with DeepL and GPT-4

## Notes

- The server generates exactly 50 jokes at startup when using GPT-4 mode
- Each client is limited to 5 translations before automatic disconnection
- The application supports concurrent translations
- Jokes are stored in memory and optionally persisted to jokes.json

## Error Handling

- Fallback to default jokes if joke generation fails
- Proper error messaging for API and connection issues
- Automatic reconnection attempts for temporary failures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

This application uses API keys for both OpenAI and DeepL services. Never commit your `.env` file or expose your API keys. The `.env` file is included in `.gitignore` to prevent accidental commits.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Clinton Gnanaraj - [@clintongnanaraj](https://github.com/clintonai-tech)

## Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4 API
- [DeepL](https://www.deepl.com/) for translation API
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework 
