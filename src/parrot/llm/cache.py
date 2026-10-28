import hashlib
import json
from pathlib import Path

from parrot.models import Verdict

CACHE_FILE = Path("cache.json")

_cache: dict[str, dict] = (
    json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
)


def _key(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()


def get(prompt: str) -> Verdict | None:
    hit = _cache.get(_key(prompt))
    return Verdict(**hit) if hit else None


def put(prompt: str, verdict: Verdict) -> None:
    _cache[_key(prompt)] = verdict.model_dump()


def save() -> None:
    CACHE_FILE.write_text(json.dumps(_cache, indent=2))