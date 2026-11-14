"""macpilot-mcp config.

Primary env prefix is MACPILOT_*. For exact-code vendor compat the index
layer still reads APPLE_MAIL_* via vendor_imdinu.config — mirror our values
there at startup so a single prefix is enough for operators.
"""

from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path.home() / ".macpilot-mcp"
DEFAULT_INDEX_PATH = APP_DIR / "index.db"


def get_index_path() -> Path:
    for key in ("MACPILOT_INDEX_PATH", "APPLE_MAIL_INDEX_PATH"):
        val = os.environ.get(key)
        if val:
            return Path(val).expanduser()
    return DEFAULT_INDEX_PATH


def get_safety_profile() -> str:
    return os.environ.get(
        "MACPILOT_SAFETY_PROFILE",
        os.environ.get("APPLE_MAIL_MCP_SAFETY_PROFILE", "safe_manage"),
    )


def get_transport() -> str:
    return os.environ.get("MACPILOT_TRANSPORT", "stdio")


def get_port(default: int = 8765) -> int:
    return int(os.environ.get("MACPILOT_PORT", str(default)))


def mirror_env_for_vendors() -> None:
    """Mirror MACPILOT_* onto APPLE_MAIL_* so vendored code keeps working."""
    path = os.environ.get("MACPILOT_INDEX_PATH")
    if path and "APPLE_MAIL_INDEX_PATH" not in os.environ:
        os.environ["APPLE_MAIL_INDEX_PATH"] = path
    elif "APPLE_MAIL_INDEX_PATH" not in os.environ:
        os.environ["APPLE_MAIL_INDEX_PATH"] = str(DEFAULT_INDEX_PATH)

    profile = os.environ.get("MACPILOT_SAFETY_PROFILE")
    if profile and "APPLE_MAIL_MCP_SAFETY_PROFILE" not in os.environ:
        os.environ["APPLE_MAIL_MCP_SAFETY_PROFILE"] = profile
