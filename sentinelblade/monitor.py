# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""SHA-256 file integrity baselines and comparisons."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASELINE_NAME = "baseline.json"


def _hash_path(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _collect_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for current_root, directory_names, file_names in os.walk(root, followlinks=False):
        directory_names[:] = [
            name for name in directory_names if not (Path(current_root) / name).is_symlink()
        ]
        for name in file_names:
            path = Path(current_root) / name
            if path.name == BASELINE_NAME and path.parent == root:
                continue
            if path.is_symlink() or not path.is_file():
                continue
            files[path.relative_to(root).as_posix()] = _hash_path(path)
    return files


def create_baseline(folder: str | Path) -> dict[str, Any]:
    """Hash files under ``folder`` and atomically write its baseline.json."""
    root = Path(folder).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")
    files = _collect_files(root)
    baseline: dict[str, Any] = {
        "version": 1,
        "algorithm": "sha256",
        "root": str(root),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    baseline_path = root / BASELINE_NAME
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False) as temp_file:
            temporary_path = temp_file.name
            json.dump(baseline, temp_file, indent=2, sort_keys=True)
            temp_file.write("\n")
        os.replace(temporary_path, baseline_path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)
    return {"command": "monitor baseline", "baseline": str(baseline_path), "file_count": len(files)}


def check_baseline(folder: str | Path) -> dict[str, Any]:
    """Compare files under ``folder`` with the previously saved baseline."""
    root = Path(folder).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")
    baseline_path = root / BASELINE_NAME
    try:
        with baseline_path.open("r", encoding="utf-8") as baseline_file:
            baseline = json.load(baseline_file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"No baseline found at {baseline_path}; run 'monitor baseline' first.") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid baseline JSON: {baseline_path}") from error
    if not isinstance(baseline, dict) or not isinstance(baseline.get("files"), dict):
        raise ValueError(f"Invalid baseline format: {baseline_path}")

    original = baseline["files"]
    current = _collect_files(root)
    old_paths = set(original)
    current_paths = set(current)
    new_files = sorted(current_paths - old_paths)
    deleted_files = sorted(old_paths - current_paths)
    modified_files = sorted(path for path in old_paths & current_paths if original[path] != current[path])
    return {
        "command": "monitor check",
        "folder": str(root),
        "new": new_files,
        "modified": modified_files,
        "deleted": deleted_files,
        "clean": not (new_files or modified_files or deleted_files),
    }
