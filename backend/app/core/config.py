"""
EcoRoute Backend - Application Configuration
============================================

Centralised settings loaded from environment variables with sensible
development defaults so the API can boot without any external config.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, List

import json
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode


PROJECT_ROOT = Path(__file__).resolve().parents[3]   # -> /home/z/my-project/ecoroute


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ------------------------------------------------------------------ #
    # App metadata
    # ------------------------------------------------------------------ #
    app_name: str = "EcoRoute API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=True, description="Enable debug mode")
    api_prefix: str = "/api/v1"

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    cors_origins: Annotated[List[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: any) -> list[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
                return [str(parsed).strip()]
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    database_url: str = Field(
        default=f"sqlite:///{PROJECT_ROOT}/data/ecoroute.db",
        description="SQLAlchemy database URL",
    )

    @property
    def safe_database_url(self) -> str:
        """Return a SQLAlchemy-compatible URL, falling back to local SQLite."""
        url = self.database_url
        if url.startswith(("sqlite:///", "postgresql://", "postgresql+psycopg2://", "mysql://", "mysql+pymysql://")):
            return url
        # Fall back to default SQLite if env var is malformed
        return f"sqlite:///{PROJECT_ROOT}/data/ecoroute.db"

    # ------------------------------------------------------------------ #
    # ML model
    # ------------------------------------------------------------------ #
    model_path: str = Field(
        default=str(PROJECT_ROOT / "ml" / "models" / "best_model.joblib"),
        description="Path to the persisted sklearn pipeline",
    )

    # ------------------------------------------------------------------ #
    # Routing (OSMnx cache)
    # ------------------------------------------------------------------ #
    osmnx_cache_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "osm_cache")
    )

    # ------------------------------------------------------------------ #
    # Analytics / simulation defaults
    # ------------------------------------------------------------------ #
    fuel_price_per_liter: float = 95.0       # INR per litre (diesel baseline)
    co2_cost_per_kg: float = 0.05            # INR carbon cost
    driver_cost_per_hour: float = 250.0      # INR per hour


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (single instance per process)."""
    return Settings()


settings = get_settings()
