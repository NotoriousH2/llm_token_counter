# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM Token Counter is a Gradio-based web application that calculates token counts for text across various LLM models (both commercial APIs and Hugging Face models). Users can input text directly or upload files (.pdf, .docx, .txt, .md) to determine token counts for cost estimation and context window management.

## Commands

### Development
```bash
# Run the server (default port 7860)
python src/server.py

# Install dependencies
pip install -r requirements.txt

# Set up virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

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

# Manual package update
bash /home/ubuntu/llm_token_counter/scripts/update_packages.sh

# View update logs
cat /home/ubuntu/llm_token_counter/logs/update.log
```

### Configuration
Create a `.env` file in the project root with API keys:
```bash
OPENAI_API_KEY="your_openai_api_key"
GOOGLE_API_KEY="your_google_api_key"
ANTHROPIC_API_KEY="your_anthropic_api_key"
HUGGINGFACE_HUB_TOKEN="your_huggingface_read_token"
```

Additional environment variables:
- `CACHE_DIR`: Hugging Face model cache directory (default: `~/.cache/huggingface`)
- `PORT`: Server port (default: `7860`)
- `HOST`: Server host (default: `0.0.0.0`)
- `LANGUAGE`: Default UI language - `kor` or `eng` (default: `kor`)

## Architecture

### Core Components

**Entry Point**: `src/server.py` launches the Gradio interface via `create_interface()` with `root_path="/tokenizer"` for nginx proxy support.

**Main Interface Logic**: `src/interface.py` contains all UI construction and the main `process_input()` function that:
1. Validates input (model name, API keys, file size)
2. Determines model type (commercial vs Hugging Face)
3. Handles file parsing or text input via helper functions
4. Routes to appropriate tokenization method
5. Updates history and model lists

**Helper Functions** (in `interface.py`):
- `validate_model_name()`, `validate_api_key_for_model()`, `validate_file_size()` - Input validation
- `parse_uploaded_file()`, `get_input_data()` - File/text processing (deduplicated)
- `create_history_entry()`, `update_history()` - History management (deduplicated)
- `count_tokens_claude()`, `count_tokens_gemini()`, `count_tokens_gpt()` - Vendor-specific counting
- `create_success_response()`, `create_error_response()` - Standardized responses

**Custom Exceptions** (in `interface.py`):
- `ValidationError`, `APIKeyMissingError`, `FileSizeExceededError`, `ModelNameError`, `InputEmptyError`

**Token Counting**:
- **Commercial models** (GPT, Claude, Gemini): Handled via helper functions using vendor-specific libraries (`tiktoken`, `anthropic`, `google.genai`)
- **Hugging Face models**: Use `core/tokenizer_loader.py` for caching tokenizers and `core/token_counter.py` for counting

**File Parsers**: `src/parsers/` directory contains specialized parsers with LRU caching:
- `pdf_parser.py` - Uses pdfplumber
- `docx_parser.py` - Uses python-docx
- `text_parser.py` - Handles .txt and .md files
- `__init__.py` - Implements `@lru_cache(maxsize=100)` with mtime-based invalidation

**Model Storage**: `src/utils/model_store.py` manages dynamic model lists in `models.json`:
- Separate lists for "official" (commercial) and "custom" (Hugging Face) models
- **mtime-based in-memory caching** to reduce disk I/O
- Thread-safe atomic writes using temporary files
- Auto-sorted alphabetically
- Models are automatically added when first used

**Multi-language Support**: `src/utils/languages.py` provides:
- `LanguageManager` class for text resource management
- `TEXT_RESOURCES` dictionary with Korean and English translations
- Error messages for validation failures (API key missing, file too large, etc.)

**Configuration**: `src/utils/config.py` uses Pydantic Settings with helper methods:
- `has_anthropic_key()`, `has_google_key()`, `has_openai_key()` - API key validation
- `get_max_file_size_bytes()` - File size limit (default: 20MB)

### Key Design Patterns

1. **Caching Strategy**:
   - Tokenizers: In-memory cache with thread-safe loading
   - Parsed files: LRU cache (max 100 entries) with mtime invalidation
   - Model lists: mtime-based cache to prevent repeated disk reads

2. **Thread Safety**: Uses locks for tokenizer loading and model list updates to prevent race conditions.

3. **Dynamic Model Lists**: Models are stored in `src/utils/models.json` and automatically updated when users try new models.

4. **Vendor-Specific Token Counting**: Commercial models require different APIs:
   - Claude: Uses exact model name, subtracts 7 template tokens
   - Gemini: Uses `client.models.count_tokens()`
   - GPT: Uses `tiktoken.encoding_for_model()`

5. **Input Validation**: All inputs validated before processing:
   - Model names checked for emptiness and minimum length
   - API keys verified before API calls
   - File sizes checked against `max_file_size_mb` setting

6. **UI State Management**: Gradio's `gr.State` manages calculation history (last 5 entries) that persists across interactions.

## Deployment

### Production Setup
- **Service**: systemd service (`tokenizer.service`)
- **Proxy**: nginx reverse proxy at `/tokenizer/` → `localhost:7860`
- **Auto-update**: Weekly cron job (Mondays 3AM UTC) updates `transformers`, `tiktoken`, `anthropic`, `google-genai`, `huggingface-hub`

### Files
- `/etc/systemd/system/tokenizer.service` - systemd service file
- `/home/ubuntu/llm_token_counter/scripts/update_packages.sh` - Package update script
- `/home/ubuntu/llm_token_counter/logs/update.log` - Update logs

## Testing

Tests are located in `tests/` directory:
- `test_model_store.py` - Model persistence and caching tests

Run tests:
```bash
PYTHONPATH=src pytest tests/ -v
```

## Important Notes

- The application supports both dropdown selection and direct model ID input for flexibility
- New models are automatically lowercase-normalized and added to the persistent model store
- File uploads are validated by extension and size (max 20MB) before parsing
- The UI dynamically shows/hides input fields based on selected model type and input method
- Commercial models must contain keywords "claude", "gemini", or "gpt" in their model ID for proper routing
- Language toggle is in top-right corner and updates all UI text dynamically
- API keys are loaded from `SETTINGS` (via `.env`), not `os.environ.get()` directly
