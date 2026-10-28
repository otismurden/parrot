# Parrot trap test

`trap_repo/` is a fake shop codebase built to break Parrot: real duplicates, traps that only look like
problems, and files that are awkward to parse. `expected.json` is the answer key; `check.py` scores
Parrot against it.

Run from `demo/`:

```bash
uv run python check.py                 # scorecard, static analysis only
uv run python check.py --llm           # also score Gemma (needs GEMINI_API_KEY)
uv run parrot scan trap_repo --no-llm
uv run python output_edge_cases.py     # odd Gemma answers through the output
```

## Results (main @ 2540c7a, static only)

20 files, 54 units, 8 duplicate groups, 30 dead suspects. **2 failing, 5 known gaps.**
Precision on the labelled cases without Gemma: 55% (6 of 11 flags are real problems).

| Area | Result |
|---|---|
| Duplicates caught | D1 renamed copy, D2 three-way copy, D3 whole-class copy (methods not double-reported), D4 tabs + CRLF copy |
| Dead code caught | X1, X2 never referenced |
| Traps handled statically | Routes, decorator registry, pyproject entry point, `__all__`, pytest fixture, dunder methods, `build/` folder |
| Robustness | Syntax error, latin-1 bytes, empty file, non-ASCII names: no crash |
| Left for Gemma | T1 same-shape unrelated rules, T3 test boilerplate, X5 planned feature |

## Still failing

| Case | Problem | Owner |
|---|---|---|
| T2 | Three one-line config getters with long docstrings are flagged as a duplicate | Duplicates |
| X8 | `handle_refund`, called via `globals()[f"handle_{type}"]`, is flagged as dead | Dead code / Gemma |
| ?? | The two `__init__` methods of the copied address classes are reported again on their own | Duplicates |

## Known gaps

D5 copy with one extra block, D6 same job written differently, D7 sync/async twins,
X3 function that only calls itself, X4 dead function hidden by a method with the same name.

## Fixed during testing

- `build/` scanned, adding fake extra copies (Lead)
- Dead-code stage was a stub (Dead code)
- Output (Albert): confidence given as `85` drew an 850-character bar and won "most confident";
  negative or >1 confidence now clamped; `[brackets]` in Gemma's text escaped; empty reason and missing
  source handled; paths shortened; `--no-llm` side-by-side ties go to the biggest copy
