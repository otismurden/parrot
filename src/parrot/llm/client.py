import asyncio
import os
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv
from google import genai
from google.genai import errors

from pydantic import ValidationError

from parrot.models import Candidate, Finding, Verdict

from . import cache
from .prompts import build_prompt

MODEL = "gemma-4-26b-a4b-it"  # check AI Studio for the newest Gemma
MAX_CONCURRENT = 5
TIMEOUT = 60  # seconds per request


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """Created lazily so --no-llm runs don't need an API key."""
    load_dotenv(find_dotenv())
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set. Add it to .env")

    return genai.Client(api_key=api_key)


async def ask(prompt: str, tries: int = 3) -> Verdict | None:
    if (hit := cache.get(MODEL, prompt)) is not None:
        return hit

    for attempt in range(tries):
        try:
            # Timed out here rather than in the SDK, whose timeout error
            # depends on which HTTP library is installed
            async with asyncio.timeout(TIMEOUT):
                resp = await get_client().aio.models.generate_content(
                    model=MODEL, contents=prompt
                )
        except TimeoutError:
            continue  # a hung request gets retried like any other failure
        except (errors.ServerError, errors.ClientError) as e:
            # 5xx = Google's problem, 429 = rate limit: wait, then retry
            if isinstance(e, errors.ClientError) and e.code != 429:
                raise  # 400/403/404 = our problem, retrying won't help
            await asyncio.sleep(2 ** attempt)  # waits 1s, 2s, 4s
            continue

        # Take the outermost {...} so code fences or chatter around it are
        # ignored
        text = resp.text or ""
        text = text[text.find("{"):text.rfind("}") + 1]
        try:
            verdict = Verdict.model_validate_json(text)
        except ValidationError:
            continue
        cache.put(MODEL, prompt, verdict)
        return verdict
    return None


async def ask_gemma_all(cands: list[Candidate]) -> list[Finding]:
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def limited(c: Candidate) -> Finding:
        async with sem:
            try:
                return Finding(c, await ask(build_prompt(c)))
            except errors.APIError:
                # One bad request shouldn't lose every other verdict
                return Finding(c, None)

    findings = await asyncio.gather(*(limited(c) for c in cands))
    cache.save()
    return list(findings)
