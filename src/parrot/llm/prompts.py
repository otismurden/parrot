# Author: Gavison
from parrot.models import Candidate, Unit

# Long units are cut so one huge class can't blow up the prompt
MAX_LINES = 80

# Doubled {{ }} are needed because these are filled with .format(code=...)
DUPE_PROMPT = """You are reviewing Python code.
Are these functions real duplicates that should be merged?
Reply with ONLY JSON: {{"is_issue": true/false, "confidence": 0-1,
"reason": "...", "suggestion": "..."}}

{code}"""

DEAD_PROMPT = """You are reviewing Python code.
Is this code really unused? Consider decorators, getattr, dynamic calls,
and anything that could be imported from elsewhere.
Reply with ONLY JSON: {{"is_issue": true/false, "confidence": 0-1,
"reason": "...", "suggestion": "..."}}

{code}"""


def _show(u: Unit) -> str:
    lines = u.source.splitlines()
    if len(lines) > MAX_LINES:
        cut = len(lines) - MAX_LINES
        lines = lines[:MAX_LINES] + [f"# ... {cut} more lines"]
    return f"# {u.kind} {u.name} at {u.id}\n" + "\n".join(lines)


def build_prompt(c: Candidate) -> str:
    template = DUPE_PROMPT if c.kind == "duplicate" else DEAD_PROMPT
    code = "\n\n".join(_show(u) for u in c.units)
    if c.context:
        code = f"Context: {c.context}\n\n{code}"
    return template.format(code=code)
