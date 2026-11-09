"""Konfigurasi terpusat. Tidak pernah gagal saat import."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]



class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

     # ── embedding ────────────────────────────────────────────
    embedding_model: str = "gemini-embedding-001"
    embedding_dim: int = 768      # 768 | 1536 | 3072
    # ─────────────────────────────────────────────────────────

    temperature: float = 0.7
    max_output_tokens: int = 1024

    history_window: int = 12       # pesan terakhir yang dikirim ke model
    summarize_every: int = 8       # ringkas tiap N pesan baru, bukan tiap turn

    rag_k: int = 3
    rag_score_threshold: float = 0.78
    rag_persist_dir: Path = ROOT / "data" / "vectorstore"
    rag_source_dir: Path = ROOT / "data" / "knowledge"

    rate_limit_messages: int = 15
    rate_limit_window: int = 60

    data_dir: Path = ROOT / "data" / "conversations"

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def configured(self) -> bool:
        return bool(self.gemini_api_key.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

    @field_validator("gemini_api_key", mode="before")
    @classmethod
    def _clean_key(cls, v: str) -> str:
        if not isinstance(v, str):
            return v
        return v.strip().strip('"').strip("'").strip()

settings = get_settings()