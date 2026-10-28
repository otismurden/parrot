from dataclasses import dataclass
from pydantic importy BaseModel

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
    kind: str
    context: str = ""

class Verdict(BaseModel):
    is_issue: bool
    confidence: float
    reason: str
    suggestion: str | None = None


class Finding:
    candidate : Candidate
    verdict: Verdict | None
    # --no-llm = None


