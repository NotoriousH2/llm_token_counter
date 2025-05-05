import json
import os
from threading import Lock

# 모델 리스트를 저장할 JSON 파일 경로 지정
MODEL_STORE_PATH = os.path.join(os.path.dirname(__file__), 'models.json')
_lock = Lock()

def _load_store():
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
        return json.load(f)

def _save_store(store):
    # 임시 파일에 쓰고 atomic replace
    tmp_path = MODEL_STORE_PATH + '.tmp'
    store['official'] = sorted(store.get('official', []))
    store['custom']   = sorted(store.get('custom', []))
    
    tmp_path = MODEL_STORE_PATH + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, MODEL_STORE_PATH)

def get_official_models():
    store = _load_store()
    return store.get("official", [])

def get_custom_models():
    store = _load_store()
    return store.get("custom", [])

def add_official_model(model_name):
    name = model_name.lower()
    with _lock:
        store = _load_store()
        if name not in store.get("official", []):
            store["official"].append(name)
            _save_store(store)

def add_custom_model(model_name):
    name = model_name.lower()
    with _lock:
        store = _load_store()
        if name not in store.get("custom", []):
            store["custom"].append(name)
            _save_store(store) 