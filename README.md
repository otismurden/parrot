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

# Limitations
- Python-only. 
