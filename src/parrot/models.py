from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class Unit:
    id: str
    path: str
    name: str
    start: int
    end: int
    source: str
    kind: str
    decorated: bool = False

@dataclass
class Candidate:
    kind: str
    units: list[Unit]
    score: float
    context: str = ""

class Verdict(BaseModel):
    is_issue: bool
    confidence: float = Field(ge=0, le=1)
    reason: str
    suggestion: str | None = None

@dataclass
class Finding:
    candidate: Candidate
    verdict: Verdict | None
