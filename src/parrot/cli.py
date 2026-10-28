from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

from parrot.pipeline import run_pipeline
from parrot.report.terminal import show

load_dotenv()

app = typer.Typer()

@app.callback()
def main():
    """
    Parrot: find duplicate and dead code using Gemma 4.

    Made by David, Otis, Gavison, Viktor, and Albert.
    """

@app.command()
def scan(path: Annotated[Path, typer.Argument(exists=True, file_okay=False)],
         no_llm: Annotated[bool, typer.Option("--no-llm")] = False,
         max_llm_calls: int = 50):
    findings = run_pipeline(path,
                            use_llm=not no_llm,
                            limit=max_llm_calls)
    show(findings)
