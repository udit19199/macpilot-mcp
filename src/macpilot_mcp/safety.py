"""Safety helpers — exact denylist logic lives in vendor_freyer.paths."""

from __future__ import annotations

from .vendor_freyer.paths import (
    allowed_attach_roots,
    allowed_write_roots,
    configure,
    validate_read_path,
    validate_write_path,
)

__all__ = [
    "allowed_attach_roots",
    "allowed_write_roots",
    "configure",
    "validate_read_path",
    "validate_write_path",
]
