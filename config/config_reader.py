"""
utilities/config_reader.py

Layered configuration reader for Playwright + pytest projects.

Lookup priority (highest to lowest):
    1. Runtime override   (ConfigReader.set_override, e.g. from a pytest option)
    2. OS environment variable
    3. .env file
    4. Default

Environment-aware lookups (SIT / UAT) try "<ENV>_<KEY>" first, then "<KEY>".
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from dotenv import dotenv_values

_MISSING: Any = object()  # sentinel: "caller gave no default"

_TRUE = {"1", "true", "yes", "y", "on"}
_FALSE = {"0", "false", "no", "n", "off"}


class ConfigError(RuntimeError):
    """Raised for missing or invalid configuration."""


def _find_dotenv(filename: str = ".env") -> Optional[Path]:
    """
    Locate the .env file independent of where pytest was launched.
    Order: $DOTENV_PATH -> walk up from CWD -> walk up from this file.
    """
    explicit = os.environ.get("DOTENV_PATH")
    if explicit:
        path = Path(explicit)
        return path if path.is_file() else None

    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for folder in (start, *start.parents):
            candidate = folder / filename
            if candidate.is_file():
                return candidate
    return None


class ConfigReader:
    SUPPORTED_ENVS = {"SIT", "UAT"}
    DEFAULT_ENV = "UAT"
    SECRET_HINTS = ("PASSWORD", "PASSWD", "SECRET", "TOKEN", "API_KEY", "KEY")

    _overrides: Dict[str, str] = {}
    _dotenv: Optional[Dict[str, Optional[str]]] = None  # lazy-loaded cache

    # ------------------------------------------------------------------ #
    # Sources
    # ------------------------------------------------------------------ #
    @classmethod
    def _load_dotenv(cls) -> Dict[str, Optional[str]]:
        if cls._dotenv is None:
            path = _find_dotenv()
            try:
                cls._dotenv = dict(dotenv_values(path)) if path else {}
            except Exception:  # malformed file -> behave like ignoreIfMalformed()
                cls._dotenv = {}
        return cls._dotenv

    @classmethod
    def reload(cls) -> None:
        """Force the .env file to be re-read (handy in tests)."""
        cls._dotenv = None

    @classmethod
    def set_override(cls, key: str, value: str) -> None:
        cls._overrides[key] = value

    @classmethod
    def clear_overrides(cls) -> None:
        cls._overrides.clear()

    # ------------------------------------------------------------------ #
    # Core lookup
    # ------------------------------------------------------------------ #
    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Plain (non environment-prefixed) lookup. Empty values are ignored."""
        for source in (cls._overrides, os.environ, cls._load_dotenv()):
            value = source.get(key)
            if value is not None and value.strip() != "":
                return value.strip()
        return default

    # ------------------------------------------------------------------ #
    # Environment support
    # ------------------------------------------------------------------ #
    @classmethod
    def env(cls) -> str:
        """Active environment (default UAT). Validates against SUPPORTED_ENVS."""
        value = (cls.get("ENV", cls.DEFAULT_ENV) or cls.DEFAULT_ENV).upper()
        if value not in cls.SUPPORTED_ENVS:
            raise ConfigError(
                f"Invalid ENV '{value}'. Supported: {sorted(cls.SUPPORTED_ENVS)}"
            )
        return value

    @classmethod
    def get_env_value(cls, key: str, default: Any = _MISSING) -> Optional[str]:
        """
        Looks up "<ENV>_<KEY>", then falls back to a global "<KEY>".

        - No default given  -> raises ConfigError if neither key exists.
        - Default given     -> returns it instead (None is allowed).
        """
        env = cls.env()
        scoped_key = f"{env}_{key}"

        value = cls.get(scoped_key)
        if value is None:
            value = cls.get(key)
        if value is not None:
            return value

        if default is _MISSING:
            raise ConfigError(
                f"Missing config key: {scoped_key} (or {key}) with ENV={env}. "
                "Check your .env file or environment variables."
            )
        return default

    # ------------------------------------------------------------------ #
    # Typed helpers (all environment-aware)
    # ------------------------------------------------------------------ #
    @classmethod
    def _typed(cls, key: str, default: Any, parser: Callable[[str], Any], type_name: str):
        raw = cls.get_env_value(key, default if default is _MISSING else None)
        if raw is None:
            return default
        try:
            return parser(raw)
        except ValueError as exc:
            raise ConfigError(f"Config key '{key}' must be {type_name}, got '{raw}'") from exc

    @classmethod
    def get_int(cls, key: str, default: Any = _MISSING) -> Optional[int]:
        return cls._typed(key, default, int, "an integer")

    @classmethod
    def get_float(cls, key: str, default: Any = _MISSING) -> Optional[float]:
        return cls._typed(key, default, float, "a number")

    @classmethod
    def get_bool(cls, key: str, default: Any = _MISSING) -> Optional[bool]:
        def parse(raw: str) -> bool:
            low = raw.lower()
            if low in _TRUE:
                return True
            if low in _FALSE:
                return False
            raise ValueError(raw)

        return cls._typed(key, default, parse, "a boolean (true/false)")

    @classmethod
    def get_list(cls, key: str, default: Any = _MISSING, sep: str = ",") -> Optional[List[str]]:
        return cls._typed(
            key, default, lambda raw: [p.strip() for p in raw.split(sep) if p.strip()], "a list"
        )

    # ------------------------------------------------------------------ #
    # Safe logging
    # ------------------------------------------------------------------ #
    @classmethod
    def masked(cls, key: str) -> str:
        """Value for logs/reports; secrets are replaced with ****."""
        value = cls.get_env_value(key, None)
        if value is None:
            return "<not set>"
        if any(hint in key.upper() for hint in cls.SECRET_HINTS):
            return "****"
        return value