from parrot.models import Candidate

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


def build_prompt(c: Candidate) -> str:
    template = DUPE_PROMPT if c.kind == "duplicate" else DEAD_PROMPT
    code = "\n\n".join(u.source for u in c.units)
    return template.format(code=code)