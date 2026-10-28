"""Precision on the trap repo's labelled cases, without and with Gemma.

    uv run python score.py            # both rows (Gemma row needs GEMINI_API_KEY)
    uv run python score.py --no-llm   # static row only
"""

import json
import os
import sys

from dotenv import find_dotenv, load_dotenv
from rich.console import Console

from check import HERE, REPO, key
from parrot.pipeline import run_pipeline

load_dotenv(find_dotenv())
console = Console()


def labelled() -> dict[frozenset, bool]:
    answers = json.loads((HERE / "expected.json").read_text())
    cases = {frozenset(c["units"]): c["final"] == "issue" for c in answers["duplicates"]}
    cases |= {frozenset([c["unit"]]): c["final"] == "issue" for c in answers["dead"]}
    return cases


def precision(use_llm: bool) -> tuple[int, int]:
    truth = labelled()
    right = flagged = 0
    for f in run_pipeline(REPO, use_llm=use_llm, limit=100):
        units = frozenset(key(u) for u in f.candidate.units)
        if units not in truth or (f.verdict and not f.verdict.is_issue):
            continue
        flagged += 1
        right += truth[units]
    return right, flagged


def row(label: str, right: int, flagged: int) -> None:
    pct = right / flagged if flagged else 0
    filled = round(pct * 20)
    colour = "green" if pct >= 0.8 else "yellow" if pct >= 0.6 else "red"
    console.print(f"{label:15} [{colour}]{'█' * filled}[/{colour}][dim]{'░' * (20 - filled)}[/dim] "
                  f"[bold]{pct:4.0%}[/bold]  [dim]{right} of {flagged} flags are real problems[/dim]")


if __name__ == "__main__":
    console.print("[bold]Precision on the trap repo[/bold] [dim](labelled cases only)[/dim]")
    row("Without Gemma", *precision(use_llm=False))
    if "--no-llm" not in sys.argv and os.getenv("GEMINI_API_KEY"):
        row("With Gemma", *precision(use_llm=True))
    elif "--no-llm" not in sys.argv:
        console.print("[dim]With Gemma     needs GEMINI_API_KEY[/dim]")
