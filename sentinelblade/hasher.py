# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""File hashing and optional digest verification."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

SUPPORTED_ALGORITHMS = ("sha256", "sha512", "md5")


def hash_file(path: str | Path, algorithm: str = "sha256", expected: str | None = None) -> dict[str, Any]:
    """Hash a file and optionally compare its digest with ``expected``."""
    normalized_algorithm = algorithm.lower().replace("-", "")
    if normalized_algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose sha256, sha512, or md5.")

    file_path = Path(path)
    hasher = hashlib.new(normalized_algorithm)
    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            hasher.update(chunk)

    digest = hasher.hexdigest()
    result: dict[str, Any] = {
        "command": "hash",
        "path": str(file_path),
        "algorithm": normalized_algorithm,
        "digest": digest,
    }
    if expected is not None:
        result["expected"] = expected.strip().lower()
        result["verified"] = digest.lower() == expected.strip().lower()
    return result
