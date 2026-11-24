
import os
from typing import Optional

from dotenv import dotenv_values

# Load .env into a dict (does NOT modify os.environ, so priorities stay explicit).
# Missing/malformed files are handled gracefully, like ignoreIfMissing()/ignoreIfMalformed().
try:
    _dotenv = dotenv_values(".env")
except Exception:
    _dotenv = {}


class ConfigReader:
    """
    Priority: CLI override (--key / CONFIG_<KEY>) > OS env var > .env file > default
    """

    # Optional runtime overrides, the Python stand-in for Java's -DKEY=value
    _overrides: dict = {}

    @classmethod
    def set_override(cls, key: str, value: str) -> None:
        """Programmatic override (e.g. from a pytest --option or conftest.py)."""
        cls._overrides[key] = value

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        # 1. Override (equivalent of System.getProperty)
        sys_prop = cls._overrides.get(key)
        if sys_prop:
            return sys_prop

        # 2. OS environment variable
        env_var = os.environ.get(key)
        if env_var:
            return env_var

        # 3. .env file
        dotenv_value = _dotenv.get(key)
        if dotenv_value:
            return dotenv_value

        # 4. Default
        return default

    # ===== environment support =====

    @classmethod
    def env(cls) -> str:
        """Active environment: SIT or UAT (default UAT)."""
        return cls.get("ENV", "UAT").strip().upper()

    @classmethod
    def get_env_value(cls, key: str, default: Optional[str] = ...) -> Optional[str]:
        """
        Reads the environment-prefixed key.
        get_env_value("BASE_URL") -> UAT_BASE_URL or SIT_BASE_URL

        If no default is passed, raises when the key is missing.
        If a default is passed (even None), returns it instead of raising.
        """
        full_key = f"{cls.env()}_{key}"

        if default is ...:  # no default supplied -> strict mode
            value = cls.get(full_key)
            if value is None:
                raise RuntimeError(
                    f"Missing config key: {full_key} (ENV={cls.env()}). "
                    "Check your .env file."
                )
            return value.strip()

        value = cls.get(full_key, default)
        return value.strip() if value is not None else None