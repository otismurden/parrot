import typer
from pathlib import pathlib

app = typer.Typer()

@app.callback()
def main():
    """
    Parrot: find duplicate and dead code using Gemma 4. Made by David, Otis, Gavison, Viktor, and Albert.
    """

@app.command()
def scan(path: Path = typer.Argument(..., exists=True, file_okay=False),
         no_llm: bool = typer.Option(False, "no-llm"),
         max_llm_calls: int = 50):
    findings = run_pipeline(path, 
                            use_llm=not no_llm, 
                            limit=max_llm_calls)
    show(findings)


