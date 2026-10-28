"""Play the 2-minute demo in this terminal, on a fixed clock, for screen recording.

Every command is typed out, really run, and its real output revealed at reading speed.
Each section starts at a fixed second, so the video lines up with DEMO_SCRIPT.md.

    uv run python run_demo.py              # record this
    uv run python run_demo.py --prompter   # rehearse: also shows who speaks and their line
"""

import os
import subprocess
import sys
import time

from dotenv import find_dotenv, load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv(find_dotenv())
console = Console(highlight=False)
HAS_KEY = bool(os.getenv("GEMINI_API_KEY"))
TYPE_DELAY = 0.04
HOLD = 2.5  # seconds the last output line stays still before the next section

# (start second, end second, speaker, title, line)
SECTIONS = [
    (0, 15, "Otis", "The problem",
     "Every codebase collects copy-pasted functions and code nobody calls. "
     "Linters flag too much, so people ignore them. Parrot finds both, then asks Gemma 4 which ones are real."),
    (15, 40, "David", "Finding duplicates",
     "First, plain static analysis. We parse every function, blank out names and values, and compare the shapes. "
     "Here register_customer, register_admin and register_staff are the same code with renamed variables. "
     "Near-copies are caught by a similarity score."),
    (40, 60, "Viktor", "Finding dead code",
     "Dead code is anything defined but never used. Decorated routes, fixtures and dunder methods are skipped. "
     "But look at the total: 38 findings, all unreviewed. That noise is why people stop reading linters."),
    (60, 90, "Gavison", "Gemma 4 checks every finding",
     "Now the same scan with Gemma 4. Each suspect goes to Gemma with its code, five at a time, cached to disk. "
     "late_fee and loyalty_bonus look identical, but Gemma marks them Distinct: different business rules. "
     "And a planned feature comes back as Future use, not delete."),
    (90, 110, "Albert", "Proof it works",
     "The output is built for decisions: a bar and one word per finding, so Redundant means act and Distinct means leave it. "
     "We tested on a trap codebase built to fool Parrot. Gemma raises precision from this, to this."),
    (110, 120, "Otis", "Try it",
     "One command, any Python repo. Parrot: find it, check it, fix it. Thanks for watching."),
]


def wait_until(t0: float, second: float) -> None:
    delay = t0 + second - time.monotonic()
    if delay > 0:
        time.sleep(delay)


def type_command(cmd: str) -> None:
    console.print("[green]parrot/demo $[/green] ", end="")
    for ch in cmd:
        console.print(ch, end="")
        time.sleep(TYPE_DELAY)
    console.print()
    time.sleep(0.4)


def run(cmd: str) -> list[str]:
    env = os.environ | {"FORCE_COLOR": "1", "COLUMNS": str(console.width), "TERM": "xterm-256color"}
    out = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True).stdout
    return [line for line in out.splitlines() if "Querying Gemma" not in line]


def reveal(lines: list[str], until: float, t0: float) -> None:
    """Print lines evenly so the last one lands HOLD seconds before `until`."""
    if not lines:
        return
    gap = max(0.0, (t0 + until - HOLD - time.monotonic()) / len(lines))
    for line in lines:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        time.sleep(gap)


def header(i: int, section: tuple, prompter: bool) -> None:
    _, _, speaker, title, line = section
    console.print(Rule(f"[dim]{i}/{len(SECTIONS)} · {title}[/dim]", style="dim", align="left"))
    if prompter:
        console.print(Panel(line, title=f"{speaker} says", border_style="magenta"))


def main(prompter: bool) -> None:
    llm = "" if HAS_KEY else " --no-llm"
    console.clear()
    t0 = time.monotonic()
    log = []

    def section(i: int) -> tuple:
        s = SECTIONS[i]
        wait_until(t0, s[0])
        log.append((s[3], time.monotonic() - t0))
        return s

    s = section(0)
    console.print(Panel("[bold]Parrot[/bold]\nFinds copy-pasted and dead Python code,\n"
                        "then asks Gemma 4 which findings are real.",
                        border_style="green", width=60))
    header(1, s, prompter)
    type_command("uv run parrot --help")
    reveal(run("uv run parrot --help"), s[1], t0)

    s = section(1)
    header(2, s, prompter)
    type_command("uv run parrot scan trap_repo --no-llm")
    lines = run("uv run parrot scan trap_repo --no-llm")
    split = next((i for i, l in enumerate(lines) if "Dead code" in l), len(lines))
    reveal(lines[:split], s[1], t0)

    s = section(2)
    header(3, s, prompter)
    reveal(lines[split:], s[1], t0)

    s = section(3)
    console.clear()
    header(4, s, prompter)
    type_command(f"uv run parrot scan trap_repo{llm}")
    reveal(run(f"uv run parrot scan trap_repo{llm}"), s[1], t0)

    s = section(4)
    console.clear()
    header(5, s, prompter)
    type_command(f"uv run python score.py{llm}")
    reveal(run(f"uv run python score.py{llm}"), s[1], t0)

    s = section(5)
    header(6, s, prompter)
    console.print(Panel("[bold]uv run parrot scan <your repo>[/bold]\n\n"
                        "github.com/otismurden/parrot\n"
                        "[dim]David · Otis · Gavison · Viktor · Albert[/dim]",
                        border_style="green", width=60))
    if not HAS_KEY:
        console.print("[dim]rehearsal: no GEMINI_API_KEY, so the Gemma steps ran with --no-llm[/dim]")
    wait_until(t0, SECTIONS[-1][1])
    log.append(("end", time.monotonic() - t0))

    timing = " · ".join(f"{name} {sec:5.1f}s" for name, sec in log)
    print(f"\n[timing] {timing}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main("--prompter" in sys.argv)
    except KeyboardInterrupt:
        console.print("\n[dim]demo stopped[/dim]")
