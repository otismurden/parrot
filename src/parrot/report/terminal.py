from rich.columns import Columns
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from parrot.models import Finding, Unit

console = Console()


def show(findings: list[Finding]) -> None:
    t = Table(title="Parrot findings")
    t.add_column("Type")
    t.add_column("Where")
    t.add_column("Gemma says")
    for f in findings:
        u = f.candidate.units[0]
        verdict = f.verdict.reason if f.verdict else "[dim]not checked[/dim]"
        t.add_row(f.candidate.kind, f"{u.path}:{u.start}", verdict)
    console.print(t)


def side_by_side(a: Unit, b: Unit) -> None:
    console.print(Columns([
        Syntax(a.source, "python", line_numbers=True, start_line=a.start),
        Syntax(b.source, "python", line_numbers=True, start_line=b.start),
    ]))
