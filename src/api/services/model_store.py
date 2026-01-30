"""
Model store service with subscriber pattern for real-time updates
"""
import json
import os
from threading import Lock
from typing import Callable, Optional, Coroutine, Any

# Path to model store JSON file
MODEL_STORE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'utils', 'models.json'
)

_lock = Lock()
_cache: Optional[dict] = None
_cache_mtime: Optional[float] = None
_version: int = 0

# Type alias for async callback
AsyncCallback = Callable[[dict, int], Coroutine[Any, Any, None]]

# Subscriber callbacks for real-time updates
_subscribers: list[Callable[[dict, int], None]] = []
_async_subscribers: list[AsyncCallback] = []


def _is_cache_valid() -> bool:
    """Check if cache is valid based on file mtime"""
    global _cache_mtime
    if _cache is None or _cache_mtime is None:
        return False
    try:
        if not os.path.exists(MODEL_STORE_PATH):
            return False
        current_mtime = os.path.getmtime(MODEL_STORE_PATH)
        return current_mtime == _cache_mtime
    except OSError:
        return False


def _load_store() -> dict:
    """Load store from cache or file"""
    global _cache, _cache_mtime, _version

    if _is_cache_valid():
        return _cache

    if not os.path.exists(MODEL_STORE_PATH):
        store = {
            "official": ["claude-3-7-sonnet", "gemini-2.0-flash", "gpt-4o"],
            "custom": [
                "meta-llama/llama-4-maverick-17b-128e-instruct",
                "microsoft/phi-4",
                "qwen/qwen2.5-7b-instruct",
                "qwen/qwen3-8b"
            ]
        }
        _save_store(store)
        return store

    with open(MODEL_STORE_PATH, 'r', encoding='utf-8') as f:
        store = json.load(f)

    _cache = store
    _cache_mtime = os.path.getmtime(MODEL_STORE_PATH)
    return store


def _save_store(store: dict) -> None:
    """Save store to file and update cache"""
    global _cache, _cache_mtime, _version

    store['official'] = sorted(store.get('official', []))
    store['custom'] = sorted(store.get('custom', []))

    # Atomic write via temp file
    tmp_path = MODEL_STORE_PATH + '.tmp'
    os.makedirs(os.path.dirname(MODEL_STORE_PATH), exist_ok=True)
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, MODEL_STORE_PATH)

    _cache = store
    _cache_mtime = os.path.getmtime(MODEL_STORE_PATH)
    _version += 1


def _notify_subscribers(store: dict, version: int) -> None:
    """Notify all subscribers of model list change"""
    for callback in _subscribers:
        try:
            callback(store, version)
        except Exception:
            pass


async def _notify_async_subscribers(store: dict, version: int) -> None:
    """Notify all async subscribers of model list change"""
    for callback in _async_subscribers:
        try:
            await callback(store, version)
        except Exception:
            pass


def subscribe(callback: Callable[[dict, int], None]) -> None:
    """Subscribe to model list changes (sync callback)"""
    _subscribers.append(callback)


def subscribe_async(callback: AsyncCallback) -> None:
    """Subscribe to model list changes (async callback)"""
    _async_subscribers.append(callback)


def unsubscribe(callback: Callable) -> None:
    """Unsubscribe from model list changes"""
    if callback in _subscribers:
        _subscribers.remove(callback)
    if callback in _async_subscribers:
        _async_subscribers.remove(callback)


def get_version() -> int:
    """Get current version number"""
    return _version


def get_official_models() -> list[str]:
    """Get list of commercial models"""
    store = _load_store()
    return store.get("official", [])


def get_custom_models() -> list[str]:
    """Get list of HuggingFace models"""
    store = _load_store()
    return store.get("custom", [])


def get_all_models() -> dict:
    """Get all models with version"""
    store = _load_store()
    return {
        "official": store.get("official", []),
        "custom": store.get("custom", []),
        "version": _version
    }


def add_official_model(model_name: str) -> bool:
    """Add a commercial model. Returns True if model was added."""
    name = model_name.lower().strip()
    with _lock:
        store = _load_store()
        if name not in store.get("official", []):
            store["official"].append(name)
            _save_store(store)
            _notify_subscribers(store, _version)
            return True
    return False


def add_custom_model(model_name: str) -> bool:
    """Add a HuggingFace model. Returns True if model was added."""
    name = model_name.lower().strip()
    with _lock:
        store = _load_store()
        if name not in store.get("custom", []):
            store["custom"].append(name)
            _save_store(store)
            _notify_subscribers(store, _version)
            return True
    return False


async def add_official_model_async(model_name: str) -> bool:
    """Add a commercial model (async version). Returns True if model was added."""
    name = model_name.lower().strip()
    added = False
    with _lock:
        store = _load_store()
        if name not in store.get("official", []):
            store["official"].append(name)
            _save_store(store)
            added = True

    if added:
        await _notify_async_subscribers(store, _version)
    return added


async def add_custom_model_async(model_name: str) -> bool:
    """Add a HuggingFace model (async version). Returns True if model was added."""
    name = model_name.lower().strip()
    added = False
    with _lock:
        store = _load_store()
        if name not in store.get("custom", []):
            store["custom"].append(name)
            _save_store(store)
            added = True

    if added:
        await _notify_async_subscribers(store, _version)
    return added


def invalidate_cache() -> None:
    """Invalidate cache (for testing)"""
    global _cache, _cache_mtime
    _cache = None
    _cache_mtime = None
