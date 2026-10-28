"""Feed show() the odd verdicts a real model returns, to prove the output survives them.

    uv run python ../demo-traps/output_edge_cases.py
"""

from parrot.models import Candidate, Finding, Unit, Verdict
from parrot.report import show, to_json


def unit(name, start, source="def f(x):\n    return x\n", path="shop/odd.py"):
    return Unit(id=f"{path}:{start}", path=path, name=name, start=start, end=start + 1, source=source, kind="function")


# model_construct skips the 0-1 check in models.py, to test the output's own clamp
CASES = [
    ("confidence as a percentage (85)", Verdict.model_construct(is_issue=True, confidence=85, reason="Copied block.", suggestion=None)),
    ("negative confidence", Verdict.model_construct(is_issue=True, confidence=-0.3, reason="Unsure.", suggestion=None)),
    ("Rich markup in the reason", Verdict(is_issue=True, confidence=0.9,
                                          reason="Use data[key] not data[bold], and [/] closes nothing.")),
    ("very long reason", Verdict(is_issue=False, confidence=0.5, reason="Because " + "this is long " * 40)),
    ("empty reason", Verdict(is_issue=True, confidence=0.81, reason="")),
    ("no verdict (parse failed)", None),
]

findings = []
for i, (label, verdict) in enumerate(CASES):
    a, b = unit(f"case_{i}_a", 10 * i + 1), unit(f"case_{i}_b", 10 * i + 5)
    findings.append(Finding(Candidate("duplicate", [a, b], 1.0, label), verdict))

findings.append(Finding(
    Candidate("duplicate", [unit("brackets_a", 90, "def f(d):\n    return d[\"[red]\"]\n"), unit("brackets_b", 95)], 1.0),
    Verdict(is_issue=True, confidence=0.99, reason="Top pick.",
            suggestion="def get(d, key='[red]'):\n    return d[key]  # [bold]not markup[/bold]"),
))
findings.append(Finding(
    Candidate("dead", [Unit(id="x", path="shop/odd.py", name="no_source", start=1, end=3, source=None, kind="function")], 1.0),
    Verdict(is_issue=True, confidence=0.9, reason="Source could not be read."),
))

show(findings)
to_json(findings)
print("json OK")
