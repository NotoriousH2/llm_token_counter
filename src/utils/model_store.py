import json
import os
from threading import Lock
from typing import Optional

# 모델 리스트를 저장할 JSON 파일 경로 지정
MODEL_STORE_PATH = os.path.join(os.path.dirname(__file__), 'models.json')
_lock = Lock()

# 캐시 상태 변수
_cache: Optional[dict] = None
_cache_mtime: Optional[float] = None


def _is_cache_valid() -> bool:
    """파일 mtime 기반 캐시 유효성 검사"""
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
    """캐시가 유효하면 캐시 반환, 아니면 파일에서 로드"""
    global _cache, _cache_mtime

    if _is_cache_valid():
        return _cache

    if not os.path.exists(MODEL_STORE_PATH):
        # 초기 모델 리스트 설정
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

    # 캐시 업데이트
    _cache = store
    _cache_mtime = os.path.getmtime(MODEL_STORE_PATH)
    return store


def _save_store(store: dict) -> None:
    """파일에 저장하고 캐시 업데이트"""
    global _cache, _cache_mtime

    store['official'] = sorted(store.get('official', []))
    store['custom'] = sorted(store.get('custom', []))

    # 임시 파일에 쓰고 atomic replace
    tmp_path = MODEL_STORE_PATH + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, MODEL_STORE_PATH)

    # 저장 후 캐시 업데이트
    _cache = store
    _cache_mtime = os.path.getmtime(MODEL_STORE_PATH)


def _invalidate_cache() -> None:
    """캐시 무효화 (테스트용)"""
    global _cache, _cache_mtime
    _cache = None
    _cache_mtime = None


def get_official_models() -> list[str]:
    """상용 모델 목록 반환"""
    store = _load_store()
    return store.get("official", [])


def get_custom_models() -> list[str]:
    """커스텀(HuggingFace) 모델 목록 반환"""
    store = _load_store()
    return store.get("custom", [])


def add_official_model(model_name: str) -> None:
    """상용 모델 추가"""
    name = model_name.lower()
    with _lock:
        store = _load_store()
        if name not in store.get("official", []):
            store["official"].append(name)
            _save_store(store)


def add_custom_model(model_name: str) -> None:
    """커스텀(HuggingFace) 모델 추가"""
    name = model_name.lower()
    with _lock:
        store = _load_store()
        if name not in store.get("custom", []):
            store["custom"].append(name)
            _save_store(store)
