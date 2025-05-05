from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.languages import KOREAN

class Settings(BaseSettings):
    cache_dir: str = "~/.cache/huggingface"
    max_file_size_mb: int = 20
    default_models: list[str] = ["gpt2", "facebook/opt-1.3b", "EleutherAI/gpt-j-6B"]
    port: int = 7860
    host: str = "0.0.0.0"
    language: str = KOREAN  # 기본 언어 설정: 한국어

    model_config = SettingsConfigDict(env_file=".env")

SETTINGS = Settings()