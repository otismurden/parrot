"""Terminal output for Parrot. Output by Albert Adrian Iovan."""

from collections import Counter
from importlib.metadata import PackageNotFoundError, version

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table

from parrot.models import Finding, Unit

console = Console()

SURE = 0.8
BAR_WIDTH = 10

# (sure issue, unsure issue, not an issue) per finding kind
LABELS = {
    "duplicate": ("Redundant", "Overlapping", "Distinct"),
    "dead": ("Unused", "Rarely needed", "Future use"),
}
COLOURS = ("red", "yellow", "blue")


def _kind(f: Finding) -> str:
    return "dead" if f.candidate.kind == "dead" else "duplicate"


def _level(f: Finding) -> int | None:
    v = f.verdict
    if v is None:
        return None
    if not v.is_issue:
        return 2
    return 0 if v.confidence >= SURE else 1


def usefulness(f: Finding) -> str:
    level = _level(f)
    if level is None:
        return "[dim]Unreviewed[/dim]"
    return f"[{COLOURS[level]}]{LABELS[_kind(f)][level]}[/{COLOURS[level]}]"


def bar(f: Finding) -> str:
    """Bar length is how much of a problem Gemma thinks this is."""
    v = f.verdict
    if v is None:
        return "[dim]" + "░" * BAR_WIDTH + "[/dim]"
    problem = v.confidence if v.is_issue else 1 - v.confidence
    filled = round(problem * BAR_WIDTH)
    colour = COLOURS[_level(f)]
    empty = "░" * (BAR_WIDTH - filled)
    return f"[{colour}]{'█' * filled}[/{colour}][dim]{empty}[/dim]"


def top_duplicate(findings: list[Finding]) -> Finding | None:
    dupes = [f for f in findings
             if _kind(f) == "duplicate" and len(f.candidate.units) >= 2]
    confirmed = [f for f in dupes if f.verdict and f.verdict.is_issue]
    if confirmed:
        return max(confirmed, key=lambda f: f.verdict.confidence)
    return max(dupes, key=lambda f: f.candidate.score, default=None)


def _version() -> str:
    try:
        return version("parrot")
    except PackageNotFoundError:
        return "dev"


def _section(title: str, findings: list[Finding]) -> None:
    console.print()
    console.print(Rule(f"[bold]{title} ({len(findings)})[/bold]",
                       align="left", characters="━"))
    grid = Table.grid(padding=(0, 2))
    grid.add_column(no_wrap=True)
    grid.add_column()
    for i, f in enumerate(findings):
        if i:
            grid.add_row("", "")
        # Paths, names and Gemma's text may contain [brackets], so escape
        # them before they reach Rich markup
        where = "\n".join(
            f"{escape(u.path)}:{u.start}  [dim]{escape(u.name)}[/dim]"
            for u in f.candidate.units)
        reason = escape(f.verdict.reason) if f.verdict else "not checked"
        grid.add_row(f"{bar(f)} {usefulness(f)}",
                     f"{where}\n[dim]{reason}[/dim]")
    console.print(grid)


def _summary(findings: list[Finding]) -> str:
    names = {0: "redundant/unused", 1: "worth a look", 2: "keep",
             None: "unreviewed"}
    counts = Counter(_level(f) for f in findings)
    parts = [f"{counts[level]} {name}"
             for level, name in names.items() if counts[level]]
    return " · ".join([f"[bold]{len(findings)} findings[/bold]", *parts])


def show(findings: list[Finding]) -> None:
    console.print(
        f"[bold]parrot[/bold] {_version()} · {len(findings)} findings")
    if not findings:
        console.print("[green]No duplicate or dead code found.[/green]")
        return

    top = top_duplicate(findings)
    if top:
        console.print()
        a, b = top.candidate.units[:2]
        side_by_side(a, b)
        if top.verdict and top.verdict.suggestion:
            console.print("[green]→ Gemma suggests:[/green] "
                          + escape(top.verdict.suggestion))

    for title, kind in (("Duplicates", "duplicate"), ("Dead code", "dead")):
        group = [f for f in findings if _kind(f) == kind]
        if group:
            _section(title, group)

    console.print()
    console.print(_summary(findings))


def side_by_side(a: Unit, b: Unit) -> None:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(*(
        Panel(Syntax(u.source, "python", line_numbers=True,
                     start_line=u.start, word_wrap=True),
              title=f"{escape(u.path)}:{u.start}", title_align="left")
        for u in (a, b)
    ))
    console.print(grid)
