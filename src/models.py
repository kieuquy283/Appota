from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


Status = Literal["ANSWER", "ABSTAIN", "CONFLICT"]


@dataclass(frozen=True)
class Citation:
    document_id: str
    title: str
    version: str
    section: str | None = None


@dataclass
class AnswerResult:
    status: Status
    answer: str
    citations: list[Citation] = field(default_factory=list)
    reason: str | None = None
    trace: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
