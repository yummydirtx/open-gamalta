"""Configuration for the Gamalta web backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    host: str = "0.0.0.0"
    port: int = 8080
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    poll_interval: float = 5.0
    command_timeout: float = 5.0

    class Config:
        env_prefix = "GAMALTA_"


settings = Settings()
