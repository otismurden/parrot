from dataclasses import dataclass
from pydantic import BaseModel

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
    confidence: float
    reason: str
    suggestion: str | None = None

@dataclass
class Finding:
    candidate: Candidate
    verdict: Verdict | None
