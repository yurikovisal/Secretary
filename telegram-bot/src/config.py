from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BOT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BOT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    channel_id: str = Field(alias="CHANNEL_ID")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        alias="OPENAI_BASE_URL",
    )
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    default_post_length: str = Field(default="medium", alias="DEFAULT_POST_LENGTH")
    post_mode: str = Field(default="draft", alias="POST_MODE")
    skill_dir: str = Field(default="skill", alias="SKILL_DIR")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> list[int]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [int(item) for item in value]
        if isinstance(value, int):
            return [value]
        text = str(value).strip()
        if not text:
            return []
        return [int(part.strip()) for part in text.split(",") if part.strip()]

    @field_validator("post_mode", mode="before")
    @classmethod
    def normalize_post_mode(cls, value: object) -> str:
        mode = str(value or "draft").strip().lower()
        if mode not in {"draft", "publish"}:
            return "draft"
        return mode

    @property
    def skill_path(self) -> Path:
        path = Path(self.skill_dir)
        if not path.is_absolute():
            path = BOT_ROOT / path
        return path.resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
