import asyncio

from rich.console import Console

from parrot.collect import collect_units
from parrot.dead.finder import find_dead
from parrot.dupes.finder import find_dupes
from parrot.llm.client import ask_gemma_all
from parrot.models import Finding

console = Console()

def run_pipeline(path, use_llm, limit):
    """
    Collect units with AST static analysis, then find duplicate and dead
    units. Only the first `limit` suspects are sent to Gemma.
    """
    units, trees = collect_units(path)

    # Suspects determined using static analysis
    suspects = find_dupes(units) + find_dead(units, trees)
    
    # No LLM for demo
    if not use_llm:
        return [Finding(s, None) for s in suspects]
    with console.status("Querying Gemma"):
        checked = asyncio.run(ask_gemma_all(suspects[:limit]))
    return checked + [Finding(s, None) for s in suspects[limit:]]


