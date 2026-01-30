"""
Model store service with subscriber pattern for real-time updates
"""
import json
import os
from threading import Lock
from typing import Callable, Optional, Coroutine, Any, TypedDict

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

# Default limit for custom models
DEFAULT_CUSTOM_MODEL_LIMIT = 20


class ModelEntry(TypedDict):
    name: str
    usage_count: int


def _migrate_store_format(store: dict) -> tuple[dict, bool]:
    """Migrate old format (string[]) to new format ({name, usage_count}[])"""
    migrated = {"official": [], "custom": []}
    changed = False

    for key in ["official", "custom"]:
        items = store.get(key, [])
        for item in items:
            if isinstance(item, str):
                migrated[key].append({"name": item, "usage_count": 0})
                changed = True
            elif isinstance(item, dict):
                migrated[key].append(item)

    return migrated, changed


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
            "official": [
                {"name": "claude-3-7-sonnet", "usage_count": 0},
                {"name": "gemini-2.0-flash", "usage_count": 0},
                {"name": "gpt-4o", "usage_count": 0}
            ],
            "custom": [
                {"name": "meta-llama/llama-4-maverick-17b-128e-instruct", "usage_count": 0},
                {"name": "microsoft/phi-4", "usage_count": 0},
                {"name": "qwen/qwen2.5-7b-instruct", "usage_count": 0},
                {"name": "qwen/qwen3-8b", "usage_count": 0}
            ]
        }
        _save_store(store)
        return store

    with open(MODEL_STORE_PATH, 'r', encoding='utf-8') as f:
        store = json.load(f)

    # Migrate old format to new format if needed
    store, migrated = _migrate_store_format(store)
    if migrated:
        _save_store(store)
        return store

    _cache = store
    _cache_mtime = os.path.getmtime(MODEL_STORE_PATH)
    return store


def _save_store(store: dict) -> None:
    """Save store to file and update cache"""
    global _cache, _cache_mtime, _version

    # Sort official models alphabetically by name
    store['official'] = sorted(
        store.get('official', []),
        key=lambda x: x['name'] if isinstance(x, dict) else x
    )
    # Sort custom models by usage_count (descending), then by name
    store['custom'] = sorted(
        store.get('custom', []),
        key=lambda x: (-x.get('usage_count', 0), x['name']) if isinstance(x, dict) else (0, x)
    )

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
    """Get list of commercial models (names only)"""
    store = _load_store()
    models = store.get("official", [])
    return [m['name'] if isinstance(m, dict) else m for m in models]


def get_custom_models(limit: int = DEFAULT_CUSTOM_MODEL_LIMIT) -> list[str]:
    """Get list of HuggingFace models (names only), sorted by usage_count, limited"""
    store = _load_store()
    models = store.get("custom", [])
    # Already sorted by usage_count descending in _save_store
    names = [m['name'] if isinstance(m, dict) else m for m in models]
    return names[:limit]


def get_all_models() -> dict:
    """Get all models with version (returns names only, custom limited to top 20)"""
    return {
        "official": get_official_models(),
        "custom": get_custom_models(DEFAULT_CUSTOM_MODEL_LIMIT),
        "version": _version
    }


def _find_model_entry(models: list, name: str) -> tuple[int, Optional[dict]]:
    """Find model entry by name. Returns (index, entry) or (-1, None) if not found."""
    for i, m in enumerate(models):
        model_name = m['name'] if isinstance(m, dict) else m
        if model_name == name:
            return i, m
    return -1, None


def add_official_model(model_name: str) -> bool:
    """Add a commercial model or increment usage. Returns True if model was new."""
    name = model_name.lower().strip()
    with _lock:
        store = _load_store()
        models = store.get("official", [])
        idx, entry = _find_model_entry(models, name)

        if idx >= 0:
            # Existing model - increment usage_count
            if isinstance(entry, dict):
                entry['usage_count'] = entry.get('usage_count', 0) + 1
            else:
                # Migrate string entry to dict
                models[idx] = {"name": name, "usage_count": 1}
            _save_store(store)
            _notify_subscribers(get_all_models(), _version)
            return False
        else:
            # New model
            store["official"].append({"name": name, "usage_count": 1})
            _save_store(store)
            _notify_subscribers(get_all_models(), _version)
            return True


def add_custom_model(model_name: str) -> bool:
    """Add a HuggingFace model or increment usage. Returns True if model was new."""
    name = model_name.lower().strip()
    with _lock:
        store = _load_store()
        models = store.get("custom", [])
        idx, entry = _find_model_entry(models, name)

        if idx >= 0:
            # Existing model - increment usage_count
            if isinstance(entry, dict):
                entry['usage_count'] = entry.get('usage_count', 0) + 1
            else:
                # Migrate string entry to dict
                models[idx] = {"name": name, "usage_count": 1}
            _save_store(store)
            _notify_subscribers(get_all_models(), _version)
            return False
        else:
            # New model
            store["custom"].append({"name": name, "usage_count": 1})
            _save_store(store)
            _notify_subscribers(get_all_models(), _version)
            return True


async def add_official_model_async(model_name: str) -> bool:
    """Add a commercial model or increment usage (async version). Returns True if model was new."""
    name = model_name.lower().strip()
    is_new = False
    with _lock:
        store = _load_store()
        models = store.get("official", [])
        idx, entry = _find_model_entry(models, name)

        if idx >= 0:
            # Existing model - increment usage_count
            if isinstance(entry, dict):
                entry['usage_count'] = entry.get('usage_count', 0) + 1
            else:
                # Migrate string entry to dict
                models[idx] = {"name": name, "usage_count": 1}
            _save_store(store)
        else:
            # New model
            store["official"].append({"name": name, "usage_count": 1})
            _save_store(store)
            is_new = True

    await _notify_async_subscribers(get_all_models(), _version)
    return is_new


async def add_custom_model_async(model_name: str) -> bool:
    """Add a HuggingFace model or increment usage (async version). Returns True if model was new."""
    name = model_name.lower().strip()
    is_new = False
    with _lock:
        store = _load_store()
        models = store.get("custom", [])
        idx, entry = _find_model_entry(models, name)

        if idx >= 0:
            # Existing model - increment usage_count
            if isinstance(entry, dict):
                entry['usage_count'] = entry.get('usage_count', 0) + 1
            else:
                # Migrate string entry to dict
                models[idx] = {"name": name, "usage_count": 1}
            _save_store(store)
        else:
            # New model
            store["custom"].append({"name": name, "usage_count": 1})
            _save_store(store)
            is_new = True

    await _notify_async_subscribers(get_all_models(), _version)
    return is_new


def invalidate_cache() -> None:
    """Invalidate cache (for testing)"""
    global _cache, _cache_mtime
    _cache = None
    _cache_mtime = None
