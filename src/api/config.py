"""
Configuration settings for the FastAPI backend
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Language codes
KOREAN = "kor"
ENGLISH = "eng"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 7860

    # File settings
    cache_dir: str = "~/.cache/huggingface"
    max_file_size_mb: int = 20

    # Language settings
    language: str = KOREAN

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    huggingface_hub_token: str = ""

    # Default models (for initial setup)
    default_models: list[str] = ["gpt2", "facebook/opt-1.3b", "EleutherAI/gpt-j-6B"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        env_file_encoding="utf-8"
    )

    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is configured"""
        return bool(self.anthropic_api_key and self.anthropic_api_key.strip())

    def has_google_key(self) -> bool:
        """Check if Google API key is configured"""
        return bool(self.google_api_key and self.google_api_key.strip())

    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key and self.openai_api_key.strip())

    def has_huggingface_token(self) -> bool:
        """Check if HuggingFace token is configured"""
        return bool(self.huggingface_hub_token and self.huggingface_hub_token.strip())

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance for backward compatibility
SETTINGS = get_settings()
