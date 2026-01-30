# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM Token Counter is a FastAPI + React web application that calculates token counts for text across various LLM models (both commercial APIs and Hugging Face models). Users can input text directly or upload files (.pdf, .docx, .txt, .md) to determine token counts for cost estimation and context window management.

**v2.0**: Migrated from Gradio to FastAPI + React for better performance, REST API support, and real-time WebSocket synchronization.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        nginx                            │
│                    /tokenizer/*                         │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│  React SPA      │◄──WebSocket─►│   FastAPI       │
│  (Static)       │             │   Backend       │
└─────────────────┘             └────────┬────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
           ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
           │ WebSocket    │    │ Model Store  │    │ Token APIs   │
           │ Hub          │    │ (shared)     │    │ (GPT/Claude  │
           │              │    │              │    │  /Gemini/HF) │
           └──────────────┘    └──────────────┘    └──────────────┘
```

## Commands

### Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Build frontend (required once)
cd frontend && npm install && npm run build && cd ..

# Run FastAPI server (v2.0)
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 7860 --reload

# Run Gradio server (legacy v1.0)
python src/server.py

# Run tests
PYTHONPATH=src pytest tests/ -v
```

### Service Management (Production)
```bash
# Service control
sudo systemctl status tokenizer    # Check status
sudo systemctl restart tokenizer   # Restart service
sudo systemctl stop tokenizer      # Stop service
sudo journalctl -u tokenizer -f    # View logs
```

### Configuration
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY="your_openai_api_key"
GOOGLE_API_KEY="your_google_api_key"
ANTHROPIC_API_KEY="your_anthropic_api_key"
HUGGINGFACE_HUB_TOKEN="your_huggingface_read_token"
```

## Directory Structure

```
llm_token_counter/
├── src/
│   ├── api/                      # FastAPI backend (v2.0)
│   │   ├── main.py               # App entry point, static file serving
│   │   ├── config.py             # Pydantic settings
│   │   ├── routes/
│   │   │   ├── tokens.py         # POST /api/count-tokens
│   │   │   ├── models.py         # GET/POST /api/models
│   │   │   └── websocket.py      # WebSocket hub
│   │   ├── services/
│   │   │   ├── token_counter.py  # Token counting logic
│   │   │   ├── model_store.py    # Shared model state with subscribers
│   │   │   └── file_parser.py    # File parsing service
│   │   └── schemas/
│   │       └── models.py         # Pydantic request/response schemas
│   ├── core/                     # Core tokenization logic
│   │   ├── tokenizer_loader.py   # HuggingFace tokenizer caching
│   │   └── token_counter.py      # Token counting function
│   ├── parsers/                  # File parsers with LRU cache
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── text_parser.py
│   ├── utils/                    # Shared utilities
│   │   ├── config.py             # Legacy config (for Gradio)
│   │   ├── pricing.py            # Model costs and context windows
│   │   ├── languages.py          # i18n for Gradio
│   │   └── model_store.py        # Legacy model store
│   ├── interface.py              # Gradio UI (legacy v1.0)
│   └── server.py                 # Gradio entry point (legacy v1.0)
├── frontend/                     # React app (v2.0)
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── hooks/                # useWebSocket, useTokenCount, useModelStore
│   │   ├── stores/               # Zustand global state
│   │   ├── i18n/                 # Korean/English translations
│   │   └── App.tsx               # Main layout
│   └── dist/                     # Production build output
├── tests/
│   ├── test_api/                 # FastAPI endpoint tests
│   └── test_model_store.py       # Model persistence tests
└── requirements.txt
```

## API Endpoints (v2.0)

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/count-tokens` | POST | Count tokens from text |
| `/api/count-tokens/file` | POST | Count tokens from uploaded file |
| `/api/models` | GET | Get model lists (official + custom) |
| `/api/models` | POST | Add a new model |
| `/api/pricing/{model}` | GET | Get pricing info for a model |
| `/api/health` | GET | Health check |

### WebSocket

```
WS /api/ws

// Server → Client (on connect)
{"type": "init", "data": {"official": [...], "custom": [...], "version": 1}}

// Server → Client (on model added)
{"type": "model_added", "data": {"official": [...], "custom": [...], "version": 2}}

// Client → Server (add model request)
{"type": "add_model", "name": "model-name", "category": "official"|"custom"}
```

## Key Components

### Backend Services

**Token Counter** (`src/api/services/token_counter.py`):
- `count_tokens_commercial()` - Routes to Claude/Gemini/GPT APIs
- `count_tokens_huggingface()` - Uses cached HuggingFace tokenizers
- Claude: Subtracts 7 template tokens
- GPT-5+: Falls back to gpt-4o tokenizer

**Model Store** (`src/api/services/model_store.py`):
- Subscriber pattern for real-time updates
- `subscribe_async()` - Register WebSocket broadcast callback
- Atomic file writes with mtime-based caching

**File Parser** (`src/api/services/file_parser.py`):
- Validates file size (max 20MB) and extension
- Supports .pdf, .docx, .txt, .md

### Frontend

**State Management**: Zustand store (`frontend/src/stores/appStore.ts`)
- Model selection, input state, results, history
- Persisted to localStorage (history, language preference)

**WebSocket Hook** (`frontend/src/hooks/useWebSocket.ts`):
- Auto-reconnect with exponential backoff
- Updates model lists in real-time

**i18n**: react-i18next with Korean/English JSON files

## Testing

```bash
# Run all tests
PYTHONPATH=src pytest tests/ -v

# API tests only
PYTHONPATH=src pytest tests/test_api/ -v
```

Test coverage:
- `test_models.py` - Model list CRUD, pricing lookup
- `test_tokens.py` - Token counting (text/file), validation
- `test_websocket.py` - WebSocket connection, model sync

## Deployment

### systemd Service
```ini
# /etc/systemd/system/tokenizer.service
[Service]
ExecStart=/path/to/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 7860 --workers 2
Environment="PYTHONPATH=/home/ubuntu/llm_token_counter/src"
```

### nginx Configuration
```nginx
location /tokenizer/ {
    proxy_pass http://localhost:7860/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    rewrite ^/tokenizer(/.*)$ $1 break;
}
```

## Important Notes

- Frontend must be built (`npm run build`) before production deployment
- WebSocket requires nginx `Upgrade` and `Connection` headers
- API keys loaded from `.env` via Pydantic Settings
- Model names are normalized to lowercase
- Commercial models identified by keywords: "claude", "gemini", "gpt", "o1", "o3"
- HuggingFace models require internet for first-time tokenizer download
