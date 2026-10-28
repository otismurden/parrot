# Author: Gavison
import hashlib
import json
import os
from pathlib import Path

from parrot.models import Verdict

# Kept in the user cache dir so it's shared no matter where parrot runs from
CACHE_FILE = (Path(os.getenv("XDG_CACHE_HOME") or Path.home() / ".cache")
              / "parrot" / "cache.json")

_cache: dict[str, dict] = (
    json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
)


def _key(model: str, prompt: str) -> str:
    # The model is part of the key so switching models doesn't reuse verdicts
    return hashlib.sha256(f"{model}\n{prompt}".encode()).hexdigest()


def get(model: str, prompt: str) -> Verdict | None:
    hit = _cache.get(_key(model, prompt))
    return Verdict(**hit) if hit else None


def put(model: str, prompt: str, verdict: Verdict) -> None:
    _cache[_key(model, prompt)] = verdict.model_dump()


def save() -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(_cache, indent=2))
