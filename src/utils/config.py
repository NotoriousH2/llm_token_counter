from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.languages import KOREAN

class Settings(BaseSettings):
    cache_dir: str = "~/.cache/huggingface"
    max_file_size_mb: int = 20
    default_models: list[str] = ["gpt2", "facebook/opt-1.3b", "EleutherAI/gpt-j-6B"]
    port: int = 7860
    host: str = "0.0.0.0"
    language: str = KOREAN  # 기본 언어 설정: 한국어

    # API 키 설정
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    huggingface_hub_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    def has_anthropic_key(self) -> bool:
        """Anthropic API 키가 설정되어 있는지 확인"""
        return bool(self.anthropic_api_key and self.anthropic_api_key.strip())

    def has_google_key(self) -> bool:
        """Google API 키가 설정되어 있는지 확인"""
        return bool(self.google_api_key and self.google_api_key.strip())

    def has_openai_key(self) -> bool:
        """OpenAI API 키가 설정되어 있는지 확인"""
        return bool(self.openai_api_key and self.openai_api_key.strip())

    def has_huggingface_token(self) -> bool:
        """HuggingFace 토큰이 설정되어 있는지 확인"""
        return bool(self.huggingface_hub_token and self.huggingface_hub_token.strip())

    def get_max_file_size_bytes(self) -> int:
        """최대 파일 크기를 바이트 단위로 반환"""
        return self.max_file_size_mb * 1024 * 1024

SETTINGS = Settings()