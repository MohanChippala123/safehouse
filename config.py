"""Configuration management for SafeHouse."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import dotenv

dotenv.load_dotenv(Path(__file__).with_name(".env"))


@dataclass
class CacheConfig:
    """Cache configuration."""

    ttl: int = 300
    max_lookup: int = 500
    max_result: int = 200


@dataclass
class APIConfig:
    """External API configuration."""

    vt_key: str = ""
    urlscan_key: str = ""
    groq_key: str = ""
    groq_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_model: str = "llama-3.1-8b-instant"


@dataclass
class LimitConfig:
    """Resource limits."""

    max_content_length: int = 50 * 1024 * 1024
    max_hops: int = 10
    max_url_length: int = 2048
    request_timeout: int = 8
    external_timeout: int = 10


@dataclass
class ServerConfig:
    """Server configuration."""

    debug: bool = False
    port: int = 5000
    workers: int = 4
    timeout: int = 120


class Config:
    """Central configuration class."""

    def __init__(self):
        self.cache = self._load_cache_config()
        self.api = self._load_api_config()
        self.limits = self._load_limit_config()
        self.server = self._load_server_config()

    @staticmethod
    def _load_cache_config() -> CacheConfig:
        return CacheConfig(
            ttl=int(os.environ.get("CACHE_TTL", "300")),
            max_lookup=int(os.environ.get("MAX_LOOKUP_CACHE", "500")),
            max_result=int(os.environ.get("MAX_RESULT_CACHE", "200")),
        )

    @staticmethod
    def _load_api_config() -> APIConfig:
        return APIConfig(
            vt_key=os.environ.get("VT_API_KEY", ""),
            urlscan_key=os.environ.get("URLSCAN_KEY", ""),
            groq_key=os.environ.get("GROQ_KEY", ""),
        )

    @staticmethod
    def _load_limit_config() -> LimitConfig:
        return LimitConfig(
            max_content_length=int(os.environ.get("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024))),
            max_hops=int(os.environ.get("MAX_HOPS", "10")),
            max_url_length=int(os.environ.get("MAX_URL_LENGTH", "2048")),
            request_timeout=int(os.environ.get("REQUEST_TIMEOUT", "8")),
            external_timeout=int(os.environ.get("EXTERNAL_TIMEOUT", "10")),
        )

    @staticmethod
    def _load_server_config() -> ServerConfig:
        return ServerConfig(
            debug=os.environ.get("FLASK_DEBUG") == "1",
            port=int(os.environ.get("PORT", "5000")),
            workers=int(os.environ.get("WORKERS", "4")),
            timeout=int(os.environ.get("TIMEOUT", "120")),
        )

    def is_production(self) -> bool:
        """Check if running in production."""
        return os.environ.get("FLASK_ENV") != "development"


config = Config()
