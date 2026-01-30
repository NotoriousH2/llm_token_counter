"""
모델별 가격 및 컨텍스트 윈도우 정보

가격은 1M 입력 토큰당 USD 기준
컨텍스트 윈도우는 토큰 단위
"""

MODEL_INFO = {
    # OpenAI models
    "gpt-5": {"input_price": 2.50, "context_window": 128000},  # Uses gpt-4o tokenizer
    "gpt-5.1": {"input_price": 2.50, "context_window": 128000},  # Uses gpt-4o tokenizer
    "gpt-5.2": {"input_price": 2.50, "context_window": 128000},  # Uses gpt-4o tokenizer
    "gpt-4o": {"input_price": 2.50, "context_window": 128000},
    "gpt-4o-mini": {"input_price": 0.15, "context_window": 128000},
    "gpt-4-turbo": {"input_price": 10.00, "context_window": 128000},
    "gpt-4": {"input_price": 30.00, "context_window": 8192},
    "gpt-3.5-turbo": {"input_price": 0.50, "context_window": 16385},
    "o1": {"input_price": 15.00, "context_window": 200000},
    "o1-mini": {"input_price": 3.00, "context_window": 128000},
    "o1-pro": {"input_price": 150.00, "context_window": 200000},
    "o3": {"input_price": 10.00, "context_window": 200000},
    "o3-mini": {"input_price": 1.10, "context_window": 200000},

    # Anthropic models
    "claude-3-5-sonnet": {"input_price": 3.00, "context_window": 200000},
    "claude-3-5-haiku": {"input_price": 0.80, "context_window": 200000},
    "claude-3-7-sonnet": {"input_price": 3.00, "context_window": 200000},
    "claude-3-opus": {"input_price": 15.00, "context_window": 200000},
    "claude-3-sonnet": {"input_price": 3.00, "context_window": 200000},
    "claude-3-haiku": {"input_price": 0.25, "context_window": 200000},
    "claude-opus-4": {"input_price": 15.00, "context_window": 200000},
    "claude-sonnet-4": {"input_price": 3.00, "context_window": 200000},

    # Google models
    "gemini-2.0-flash": {"input_price": 0.10, "context_window": 1000000},
    "gemini-2.0-flash-lite": {"input_price": 0.075, "context_window": 1000000},
    "gemini-1.5-pro": {"input_price": 1.25, "context_window": 2000000},
    "gemini-1.5-flash": {"input_price": 0.075, "context_window": 1000000},
    "gemini-2.5-pro": {"input_price": 1.25, "context_window": 1000000},
    "gemini-2.5-flash": {"input_price": 0.15, "context_window": 1000000},
}


def get_model_info(model_name: str) -> dict | None:
    """
    모델 정보 조회 (부분 매칭 지원)

    Args:
        model_name: 모델 이름 (정규화된 lowercase)

    Returns:
        {"input_price": float, "context_window": int} 또는 None
    """
    # 정확한 매칭
    if model_name in MODEL_INFO:
        return MODEL_INFO[model_name]

    # 부분 매칭 (예: claude-3-5-sonnet-20241022 → claude-3-5-sonnet)
    for key in MODEL_INFO:
        if key in model_name or model_name.startswith(key):
            return MODEL_INFO[key]

    return None


def calculate_cost(model_name: str, token_count: int) -> float | None:
    """
    예상 비용 계산

    Args:
        model_name: 모델 이름
        token_count: 토큰 수

    Returns:
        USD 비용 또는 None (가격 정보 없음)
    """
    info = get_model_info(model_name)
    if info is None:
        return None

    # 1M 토큰당 가격을 토큰당 가격으로 변환 후 계산
    return (info["input_price"] / 1_000_000) * token_count


def get_context_usage(model_name: str, token_count: int) -> tuple[float, int] | None:
    """
    컨텍스트 윈도우 사용률 계산

    Args:
        model_name: 모델 이름
        token_count: 토큰 수

    Returns:
        (사용률 %, 컨텍스트 윈도우 크기) 또는 None
    """
    info = get_model_info(model_name)
    if info is None:
        return None

    context_window = info["context_window"]
    usage_percent = (token_count / context_window) * 100
    return (usage_percent, context_window)


def format_context_window(size: int) -> str:
    """
    컨텍스트 윈도우 크기를 읽기 쉬운 형식으로 변환

    Args:
        size: 토큰 수

    Returns:
        "128K", "1M" 등의 형식
    """
    if size >= 1_000_000:
        return f"{size // 1_000_000}M"
    elif size >= 1000:
        return f"{size // 1000}K"
    return str(size)
