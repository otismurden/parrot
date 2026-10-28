# Parrot demo script (2:00)

`run_demo.py` plays the terminal side on a fixed clock: it types each command, really runs it,
and reveals the real output at reading speed. Every section starts on the second below,
so speak over the recording in this order.

| Time | Speaker | On screen | Says |
|---|---|---|---|
| 0:00–0:15 | **Otis** | Title card, `parrot --help` | Every codebase collects copy-pasted functions and code nobody calls. Linters flag too much, so people ignore them. Parrot finds both, then asks Gemma 4 which ones are real. |
| 0:15–0:40 | **David** | `parrot scan trap_repo --no-llm`: side-by-side, then the Duplicates list | First, plain static analysis. We parse every function, blank out names and values, and compare the shapes. Here register_customer, register_admin and register_staff are the same code with renamed variables. Near-copies are caught by a similarity score. |
| 0:40–1:00 | **Viktor** | Dead code list scrolls, ends on "38 findings · 38 unreviewed" | Dead code is anything defined but never used. Decorated routes, fixtures and dunder methods are skipped. But look at the total: 38 findings, all unreviewed. That noise is why people stop reading linters. |
| 1:00–1:30 | **Gavison** | Same scan with Gemma: bars and labels | Now the same scan with Gemma 4. Each suspect goes to Gemma with its code, five at a time, cached to disk. late_fee and loyalty_bonus look identical, but Gemma marks them Distinct: different business rules. And a planned feature comes back as Future use, not delete. |
| 1:30–1:50 | **Albert** | `score.py`: precision without vs with Gemma | The output is built for decisions: a bar and one word per finding, so Redundant means act and Distinct means leave it. We tested on a trap codebase built to fool Parrot. Gemma raises precision from this, to this. |
| 1:50–2:00 | **Otis** | Closing card with the repo and names | One command, any Python repo. Parrot: find it, check it, fix it. Thanks for watching. |

Gavison's and Albert's lines describe Gemma's answers. After the warm-up run below, check that
`late_fee`/`loyalty_bonus` really say **Distinct** and `award_loyalty_points` says **Future use**, and
note the two precision numbers. If Gemma says something else, change the line to match what's on screen.

## Before recording

From the repo root:

```bash
cp .env.example .env            # paste GEMINI_API_KEY
cd demo
uv run parrot scan trap_repo    # warm-up: fills demo/cache.json so the recording makes no slow API calls
uv run python score.py          # check both precision rows appear
```

- Terminal about 120×40, large font, dark theme, notifications off
- Run the warm-up from `demo/`, because the cache file is created in the current folder

## Record

```bash
cd demo
uv run python run_demo.py --prompter   # rehearse: shows each speaker's line on screen
uv run python run_demo.py              # record this one
```

Start the screen recording, then press Enter on the command. When it finishes, the terminal prints
a `[timing]` line with each section's start second; if they read 0, 15, 40, 60, 90, 110 and end 120,
the video matches this script. Without an API key the Gemma steps fall back to `--no-llm` and a
"rehearsal" note is shown, so always record with the key set.
