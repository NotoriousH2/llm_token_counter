"""
Token counting service - handles all token counting logic
"""
import anthropic
from google import genai
import tiktoken
from typing import Optional

from api.config import SETTINGS
from core.tokenizer_loader import load_tokenizer
from core.token_counter import count_tokens
from utils.pricing import calculate_cost, get_context_usage


class APIKeyMissingError(Exception):
    """Raised when required API key is missing"""
    pass


class UnsupportedModelError(Exception):
    """Raised when model is not supported"""
    pass


def validate_api_key_for_model(model_name: str) -> None:
    """
    Validate that required API key exists for the model

    Args:
        model_name: Normalized model name

    Raises:
        APIKeyMissingError: If API key is not configured
    """
    if "claude" in model_name:
        if not SETTINGS.has_anthropic_key():
            raise APIKeyMissingError("Anthropic API key not configured")
    elif "gemini" in model_name:
        if not SETTINGS.has_google_key():
            raise APIKeyMissingError("Google API key not configured")


def count_tokens_claude(model_name: str, text: str) -> int:
    """
    Count tokens using Anthropic API

    Args:
        model_name: Claude model name
        text: Text to count tokens for

    Returns:
        Token count
    """
    client = anthropic.Anthropic(api_key=SETTINGS.anthropic_api_key)
    response = client.messages.count_tokens(
        model=model_name.replace('.', '-'),
        system="",
        messages=[{"role": "user", "content": text}],
    )
    # Remove template cost (7 tokens)
    return response.input_tokens - 7


def count_tokens_gemini(model_name: str, text: str) -> int:
    """
    Count tokens using Google Gemini API

    Args:
        model_name: Gemini model name
        text: Text to count tokens for

    Returns:
        Token count
    """
    client = genai.Client(api_key=SETTINGS.google_api_key)
    response = client.models.count_tokens(
        model=model_name,
        contents=text
    )
    return response.total_tokens


def count_tokens_gpt(model_name: str, text: str) -> int:
    """
    Count tokens using tiktoken

    Args:
        model_name: GPT model name
        text: Text to count tokens for

    Returns:
        Token count
    """
    try:
        encoder = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # New models (gpt-5, etc.) use gpt-4o tokenizer
        encoder = tiktoken.encoding_for_model("gpt-4o")
    return len(encoder.encode(text))


def is_commercial_model(model_name: str) -> bool:
    """Check if model is a commercial model"""
    keywords = ["claude", "gemini", "gpt"]
    return (
        any(kw in model_name for kw in keywords) or
        model_name.startswith("o1") or
        model_name.startswith("o3")
    )


def count_tokens_commercial(model_name: str, text: str) -> int:
    """
    Count tokens for commercial models

    Args:
        model_name: Normalized model name
        text: Text to count tokens for

    Returns:
        Token count

    Raises:
        APIKeyMissingError: If API key is missing
        UnsupportedModelError: If model is not supported
        Exception: API errors
    """
    if "claude" in model_name:
        validate_api_key_for_model(model_name)
        return count_tokens_claude(model_name, text)

    elif "gemini" in model_name:
        validate_api_key_for_model(model_name)
        return count_tokens_gemini(model_name, text)

    elif "gpt" in model_name or model_name.startswith("o1") or model_name.startswith("o3"):
        return count_tokens_gpt(model_name, text)

    else:
        raise UnsupportedModelError(f"Unsupported commercial model: {model_name}")


def count_tokens_huggingface(model_name: str, text: str) -> int:
    """
    Count tokens using HuggingFace tokenizer

    Args:
        model_name: HuggingFace model name
        text: Text to count tokens for

    Returns:
        Token count
    """
    tokenizer = load_tokenizer(model_name)
    return count_tokens(tokenizer, text)


def count_tokens_for_model(
    model_name: str,
    text: str,
    is_commercial: bool
) -> dict:
    """
    Main function to count tokens for any model

    Args:
        model_name: Model name
        text: Text to count tokens for
        is_commercial: Whether it's a commercial model

    Returns:
        Dict with token_count, cost_usd, context_window, context_usage_percent
    """
    normalized_name = model_name.lower().strip()

    if is_commercial:
        token_count = count_tokens_commercial(normalized_name, text)
    else:
        token_count = count_tokens_huggingface(normalized_name, text)

    # Calculate cost and context usage
    cost = calculate_cost(normalized_name, token_count)
    context_result = get_context_usage(normalized_name, token_count)

    result = {
        "token_count": token_count,
        "cost_usd": cost,
        "context_window": None,
        "context_usage_percent": None,
        "model": normalized_name
    }

    if context_result:
        usage_percent, context_window = context_result
        result["context_window"] = context_window
        result["context_usage_percent"] = round(usage_percent, 4)

    return result
