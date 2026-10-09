from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    data_path: str = "data/procurements.jsonl"
    high_value_threshold: float = 1_000_000.0

    # Prozorro API Settings
    prozorro_api_base_url: HttpUrl = HttpUrl("https://public-api.prozorro.gov.ua/api/2.5")
    prozorro_timeout: int = 30


settings = Settings()
