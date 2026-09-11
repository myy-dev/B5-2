from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Commit:
    """기존 커밋을 부모로 참조하는 커밋 노드"""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]
