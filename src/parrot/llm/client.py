from parrot.models import Candidate, Finding


async def ask_gemma_all(cands: list[Candidate]) -> list[Finding]:
    return [Finding(c, None) for c in cands]
