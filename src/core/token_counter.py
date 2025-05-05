from transformers import PreTrainedTokenizerBase

def count_tokens(tokenizer: PreTrainedTokenizerBase, text: str) -> int:
    """토크나이저와 텍스트를 입력받아 토큰 수를 반환합니다."""
    if not text:
        return 0
    encoding = tokenizer(text)
    return len(encoding['input_ids']) 