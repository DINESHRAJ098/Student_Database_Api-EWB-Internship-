from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Students Database CRUD API"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./students.db"
    
    # Ollama AI Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma4:12b"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
