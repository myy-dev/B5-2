from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Commit:
    """A commit node whose parent edges always point to older commits."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]
