import json
from dataclasses import asdict

from parrot.models import Finding


def to_json(findings: list[Finding]) -> str:
    # asdict can't serialise the pydantic Verdict, so it is dumped separately
    return json.dumps(
        [
            {
                "candidate": asdict(f.candidate),
                "verdict": f.verdict.model_dump() if f.verdict else None,
            }
            for f in findings
        ],
        indent=2,
    )
