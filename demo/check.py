"""Score Parrot against the trap repo's answer key.

Run from the parrot repo so the package is importable:
    uv run python ../demo-traps/check.py          # static analysis only
    uv run python ../demo-traps/check.py --llm    # also score Gemma's verdicts (needs GEMINI_API_KEY)
"""

import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from parrot.collect import collect_units
from parrot.dead.finder import find_dead
from parrot.dupes.finder import find_dupes
from parrot.models import Finding

HERE = Path(__file__).parent
REPO = HERE / "trap_repo"
console = Console()


def key(u) -> str:
    p = Path(u.path)
    rel = p.resolve().relative_to(REPO.resolve()) if p.is_absolute() else p
    return f"{rel.as_posix()}::{u.name}"


def judge(findings: list[Finding] | None) -> dict[frozenset, Finding]:
    return {frozenset(key(u) for u in f.candidate.units): f for f in findings or []}


def static_result(expected: str, found: bool, built: bool) -> str:
    if not built:
        return "[magenta]NOT BUILT[/]"
    if expected == "gap":
        return "[green]CAUGHT (bonus)[/]" if found else "[yellow]KNOWN GAP[/]"
    ok = found == (expected == "flag")
    return "[green]PASS[/]" if ok else "[red]FAIL[/]"


def final_result(expected: str, f: Finding | None, llm: bool) -> str:
    if not llm:
        return "[dim]-[/]"
    if f is None:
        return "[dim]not sent[/]"
    if f.verdict is None:
        return "[red]NO VERDICT[/]"
    ok = f.verdict.is_issue == (expected == "issue")
    return ("[green]PASS[/]" if ok else "[red]FAIL[/]") + f" [dim]{f.verdict.confidence:.2f}[/]"


def main(llm: bool) -> int:
    answers = json.loads((HERE / "expected.json").read_text())
    try:
        units, trees = collect_units(REPO)
        crashed = None
    except Exception as e:  # the scan itself is under test
        units, trees, crashed = [], [], e

    dupes = find_dupes(units) if units else []
    dead = find_dead(units, trees) if units else []
    suspects = dupes + dead
    findings = suspects
    if llm:
        import asyncio
        from parrot.llm.client import ask_gemma_all
        findings = asyncio.run(ask_gemma_all(suspects))
    else:
        findings = [Finding(c, None) for c in suspects]

    dupe_map = judge([f for f in findings if f.candidate.kind == "duplicate"])
    dead_map = {next(iter(k)): f for k, f in judge([f for f in findings if f.candidate.kind == "dead"]).items()}
    dead_built = bool(dead)

    t = Table(title="Parrot vs the trap repo", title_justify="left")
    for col in ("Case", "What it tests", "Static", "With Gemma", "Fix owner"):
        t.add_column(col)

    fails = 0
    for case in answers["duplicates"]:
        want = frozenset(case["units"])
        exact = dupe_map.get(want)
        overlap = next((f for k, f in dupe_map.items() if want <= k and k != want), None)
        res = static_result(case["static"], exact is not None, True)
        if exact is None and overlap is not None:
            extra = sorted(frozenset(key(u) for u in overlap.candidate.units) - want)
            res = f"[red]FAIL[/] [dim]+{len(extra)} extra: {extra[0]}[/]"
        fails += "FAIL" in res
        t.add_row(case["id"], case["why"], res, final_result(case["final"], exact or overlap, llm), case["owner"])

    for case in answers["dead"]:
        f = dead_map.get(case["unit"])
        res = static_result(case["static"], f is not None, dead_built)
        fails += "FAIL" in res
        t.add_row(case["id"], case["why"], res, final_result(case["final"], f, llm), case["owner"])

    scanned = {key(u).split("::")[0] for u in units} if not crashed else set()
    for case in answers["collect"]:
        if case["check"] == "no_build":
            bad = sorted(p for p in scanned if p.startswith("build/"))
            res = "[green]PASS[/]" if not bad else f"[red]FAIL[/] [dim]scanned {bad[0]}[/]"
        else:
            res = "[green]PASS[/]" if not crashed else f"[red]FAIL[/] [dim]{type(crashed).__name__}: {crashed}[/]"
        fails += "FAIL" in res
        t.add_row(case["id"], case["why"], res, "[dim]-[/]", case["owner"])

    known = {k for c in answers["duplicates"] for k in [frozenset(c["units"])]}
    for k, f in dupe_map.items():
        if k not in known and not any(k >= w for w in known):
            t.add_row("??", "Unexpected duplicate: " + ", ".join(sorted(k)), "[yellow]REVIEW[/]", "", "")

    console.print(t)
    console.print(f"Scanned {len(scanned)} files, {len(units)} units, "
                  f"{len(dupes)} duplicate groups, {len(dead)} dead suspects. "
                  f"[bold red]{fails} failing[/]" if fails else "[bold green]all checks pass[/]")
    if not dead_built:
        console.print("[magenta]find_dead returned nothing: the dead-code stage is still a stub.[/]")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main("--llm" in sys.argv))
