# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Terminal branding and portable ANSI color helpers."""

from __future__ import annotations

import sys

from . import __author__, __version__

_CYAN = "\033[96m"
_SILVER = "\033[37m"
_RESET = "\033[0m"


def color(text: str, code: str, *, stream: object = sys.stdout) -> str:
    """Return colored text when the target stream supports terminal colors."""
    if not getattr(stream, "isatty", lambda: False)() or "NO_COLOR" in __import__("os").environ:
        return text
    return f"{code}{text}{_RESET}"


def print_banner() -> None:
    """Print the SentinelBlade sword banner and project attribution."""
    sword = (
        "       /\\\n"
        "      /  \\\n"
        "     /____\\\n"
        "        ||\n"
        "    ____||____\n"
        "        ||\n"
        "        ||\n"
        "        ||\n"
        "       /__\\"
    )
    print(color(sword, _CYAN))
    print(color(f"  SENTINELBLADE v{__version__} | Forge your defense.", _SILVER))
    print(color(f"  Author: {__author__}", _SILVER))
