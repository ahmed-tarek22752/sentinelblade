# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Timestamped JSON and plain-text report export."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_report(data: dict[str, Any], output: str | Path) -> Path:
    """Write ``data`` as timestamped JSON or TXT based on the output suffix."""
    destination = Path(output).expanduser()
    extension = destination.suffix.lower()
    if extension not in {".json", ".txt"}:
        raise ValueError("Report output must end in .json or .txt.")
    payload = dict(data)
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if extension == ".json":
        contents = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    else:
        contents = "SentinelBlade Report\n"
        contents += f"Generated: {payload['generated_at']}\n\n"
        contents += json.dumps(payload, indent=2, sort_keys=True) + "\n"
    destination.write_text(contents, encoding="utf-8")
    return destination


def load_report(input_path: str | Path) -> dict[str, Any]:
    """Load a JSON result for conversion with the ``report`` subcommand."""
    try:
        with Path(input_path).expanduser().open("r", encoding="utf-8") as report_file:
            data = json.load(report_file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON report: {input_path}") from error
    if not isinstance(data, dict):
        raise ValueError("A report input must contain a JSON object.")
    return data
