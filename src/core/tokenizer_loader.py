from transformers import AutoTokenizer
from huggingface_hub import hf_hub_download
import threading
import os
from utils.config import SETTINGS

_tokenizer_lock = threading.Lock()
_tokenizer_cache: dict[str, AutoTokenizer] = {}

def load_tokenizer(model_id: str) -> AutoTokenizer:
    '''주어진 모델 ID에 대해 토크나이저를 로드하거나 캐시에서 가져옵니다.'''
    if model_id in _tokenizer_cache:
        return _tokenizer_cache[model_id]

    with _tokenizer_lock:
        if model_id in _tokenizer_cache:
            return _tokenizer_cache[model_id]
        # 캐시 경로 설정
        cache_dir = os.path.expanduser(SETTINGS.cache_dir)
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            use_fast=True
        )
        _tokenizer_cache[model_id] = tokenizer
        return tokenizer 