"""Compliance filters for USDT / crypto ad copy."""

from __future__ import annotations

import re

FORBIDDEN_PATTERNS = [
    r"guaranteed\s+(profit|returns?|roi)",
    r"\bx\s?100\b",
    r"risk[\s-]?free",
    r"get\s+rich\s+quick",
    r"doubl(e|ing)\s+your\s+money",
    r"no\s+risk",
    r"100%\s+profit",
    r"flash\s+usdt",  # known scam pattern
]

_COMPILED = [re.compile(p, re.I) for p in FORBIDDEN_PATTERNS]


def is_safe_copy(text: str) -> tuple[bool, list[str]]:
    hits: list[str] = []
    for pat in _COMPILED:
        if pat.search(text):
            hits.append(pat.pattern)
    return (len(hits) == 0, hits)


def sanitize_or_raise(text: str) -> str:
    ok, hits = is_safe_copy(text)
    if not ok:
        raise ValueError(f"Compliance fail: {hits}")
    return text.strip()
