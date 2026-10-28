Parrot finds duplicate and dead Python code, using static analysis and Google's Gemma (gemma-4-26b-a4b-it) to eliminate false positives based on a confidence metric.

# Pipeline
1. Read every function and class in a specified repo using Python's **ast** module.
2. Duplicates are identified by eliminating function names and values and grouping matching outputs. Functions under 5 lines are ignored (excluding docstrings) to avoid configuration functions being eliminated.
3. 'Dead' code is identified by scanning names used in the repo and matching them to functions. If a function goes without being mentioned, it is flagged.
4. Send the suspects to Gemma (up to --max-llm-calls). Gemma replies by analysing each function and identifying if it's a real problem.
5. Show each finding with a label. 

# Setup:
- Python 3.12+ and uv.
- cp .env.example .env, then paste in a GEMINI_API_KEY from aistudio.google.com.
- uv run python scripts/check_gemma.py to confirm the key is working.

# Usage:
- uv run parrot scan <path>
- --no-llm: static analysis only, no API key needed.
- --max-llm-calls N: the most findings sent to Gemma.
- --json: machine-readable output.

# Reading the output
The scan opens with the strongest duplicate side by side and Gemma's suggested fix, then lists
duplicates and dead code separately. Each finding gets a bar (how much of a problem it is) and a word:

| Gemma's verdict | Duplicate | Dead code |
|---|---|---|
| Issue, confidence ≥ 0.8 | Redundant | Unused |
| Issue, below 0.8 | Overlapping | Rarely needed |
| Not an issue | Distinct | Future use |
| Not checked (`--no-llm`) | Unreviewed | Unreviewed |

The words come from fixed thresholds in `report/terminal.py`; the output makes no API calls of its own.

# Testing
`demo/trap_repo` is a fake shop codebase built to fool Parrot: real duplicates, traps that only look
like problems (framework routes, fixtures, `__all__` exports, functions called through `globals()`,
planned features), and awkward files (syntax errors, latin-1 bytes, tabs and CRLF, a `build/` copy).
`demo/expected.json` is the answer key.

```bash
cd demo
uv run python check.py            # scorecard per trap: PASS / FAIL / KNOWN GAP
uv run python check.py --llm      # also score Gemma's verdicts
uv run python score.py            # precision without vs with Gemma
uv run python output_edge_cases.py
```

Results and known gaps are in `demo/TEST_REPORT.md`.

# Demo
`demo/run_demo.py` plays the 2-minute demo in the terminal on a fixed clock, for screen recording.
The script, speakers and setup are in `demo/DEMO_SCRIPT.md`.

# Limitations
- Python-only. 
- Copies with an extra block, the same logic written differently, and sync/async twins are not
  caught yet (see `demo/TEST_REPORT.md`).
