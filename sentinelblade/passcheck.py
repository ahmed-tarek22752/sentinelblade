# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Password strength analysis without retaining the supplied password."""

from __future__ import annotations

import math
import string
from typing import Any

COMMON_PASSWORDS = frozenset(
    {
        "123456", "123456789", "12345678", "password", "password1",
        "qwerty", "qwerty123", "admin", "letmein", "welcome",
        "iloveyou", "abc123", "monkey", "dragon", "111111",
        "sunshine", "princess", "football", "trustno1", "passw0rd",
    }
)


def check_password(password: str) -> dict[str, Any]:
    """Return strength metrics and tips without including the password itself."""
    has_upper = any(character.isupper() for character in password)
    has_lower = any(character.islower() for character in password)
    has_digit = any(character.isdigit() for character in password)
    has_symbol = any(not character.isalnum() for character in password)
    common = password.casefold() in COMMON_PASSWORDS

    pool_size = 0
    if has_lower:
        pool_size += len(string.ascii_lowercase)
    if has_upper:
        pool_size += len(string.ascii_uppercase)
    if has_digit:
        pool_size += len(string.digits)
    if has_symbol:
        pool_size += len(string.punctuation)
    entropy = len(password) * math.log2(pool_size) if password and pool_size else 0.0

    score = min(len(password) * 3, 36)
    score += 14 if len(password) >= 12 else 0
    score += 12 if len(password) >= 16 else 0
    score += 8 if has_upper else 0
    score += 8 if has_lower else 0
    score += 8 if has_digit else 0
    score += 8 if has_symbol else 0
    score += min(int(entropy / 5), 6)
    if common:
        score = min(score, 10)
    score = min(score, 100)

    tips: list[str] = []
    if common:
        tips.append("Avoid common passwords and predictable variations.")
    if len(password) < 12:
        tips.append("Use at least 12 characters; a longer passphrase is better.")
    if not has_upper:
        tips.append("Add uppercase letters.")
    if not has_lower:
        tips.append("Add lowercase letters.")
    if not has_digit:
        tips.append("Add digits.")
    if not has_symbol:
        tips.append("Add symbols or punctuation.")
    if not tips:
        tips.append("Good mix. Prefer a unique passphrase of 16 or more characters.")

    return {
        "command": "passcheck",
        "length": len(password),
        "checks": {
            "uppercase": has_upper,
            "lowercase": has_lower,
            "digits": has_digit,
            "symbols": has_symbol,
            "common_password": common,
        },
        "entropy_bits_estimate": round(entropy, 1),
        "score": score,
        "tips": tips,
    }
