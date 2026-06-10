from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class LLMConfig(BaseSettings):
    provider: str = Field(default="openai", description="openai | anthropic | ollama")
    model: str = Field(default="gpt-4o")
    api_key: str = Field(default="")
    base_url: str = Field(default="")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)

    model_config = SettingsConfigDict(env_prefix="llm_")


class DatabaseConfig(BaseSettings):
    url: str = Field(default=f"sqlite+aiosqlite:///{PROJECT_ROOT / 'studyagent.db'}")
    pool_size: int = Field(default=5, ge=1)
    max_overflow: int = Field(default=10, ge=0)

    model_config = SettingsConfigDict(env_prefix="database_")


class ServerConfig(BaseSettings):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    debug: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="server_")


class AgentConfig(BaseSettings):
    max_steps: int = Field(default=10, ge=1)
    streaming: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="agent_")


class EpayConfig(BaseSettings):
    enabled: bool = Field(default=False)
    pid: str = Field(default="")
    key: str = Field(default="")
    gateway_url: str = Field(default="https://epay.example.com")
    notify_url: str = Field(default="")
    return_url: str = Field(default="")
    sign_type: str = Field(default="MD5")

    model_config = SettingsConfigDict(env_prefix="epay_")


class AppConfig(BaseSettings):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    epay: EpayConfig = Field(default_factory=EpayConfig)
    redis_url: str = Field(default="")
    rate_limit_rpm: int = Field(default=60, ge=1)

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


def load_config() -> AppConfig:
    return AppConfig()
