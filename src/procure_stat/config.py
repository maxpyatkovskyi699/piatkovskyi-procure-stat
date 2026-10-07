from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_path: str = "data/procurements.jsonl"
    log_level: str = "INFO"
    high_value_threshold: int = 1_000_000


settings = Settings()
