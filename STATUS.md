# STATUS.md

**Project:** jargon-simplifier-cli - a Python CLI that rewrites stiff prose
into plain English with a side-by-side diff and a glossary of swapped terms.
**Built by:** Asdale Dynamics, LLC. **License:** MIT (`Copyright (c) 2026 Asdale Dynamics, LLC`).

## What was built

- `jargon_simplifier/glossary.py` - hand-maintained jargon glossary
  (legal, medical-admin, general business, stiff-phrasing entries), each term
  with a plain-swap wording and a short definition.
- `jargon_simplifier/engine.py` - offline rule-based rewriter. Mechanical
  whole-phrase swaps with case preservation; `legal` / `medical` tones keep
  the original term in parentheses on first use; `grade-6` reading level
  splits long sentences at existing punctuation; a cleanup pass tidies
  whitespace/punctuation debris left by removals. Never invents words.
- `jargon_simplifier/llm.py` - optional LLM pass against any
  OpenAI-compatible endpoint (default Ollama `http://localhost:11434/v1`,
  configurable via `--url` / `JARGON_BASE_URL`, `--model` / `JARGON_MODEL`).
  Strict no-additions system prompt. Fallback rules: unreachable/timeout,
  empty or blank completion, refusal-shaped completion, or any SDK error all
  drop to the offline engine, noted in the report. Configured by base URL
  only - there is no key parameter, flag, or credential anywhere in the tool.
- `jargon_simplifier/reporting.py` - side-by-side (or unified/plain) diff
  plus a glossary table of every swapped term (term -> plain swap,
  definition, domain, count).
- `jargon_simplifier/cli.py` - argparse CLI (`jargon-simplifier`, also
  runnable as `python -m jargon_simplifier`). Output goes to stdout only;
  nothing overwrites without an explicit flag (`--write` in-place, `-o` +
  `--overwrite` for clobbering an existing target).
- Tests: `tests/` - 31 pytest cases covering the glossary, offline engine,
  the LLM pass through a **mocked endpoint** (success, timeout, empty,
  refusal, quoted wrappers, offline flag), and CLI end-to-end behavior
  (formats, file creation, overwrite refusal, in-place `--write`, stdin,
  fallback note).
- Docs and packaging: `README.md` (credits Asdale Dynamics, LLC),
  `LICENSE` (MIT with the exact required copyright line), `pyproject.toml`
  (console script + `[dev]` extras), `.gitignore`, `samples/lease-notice.txt`.

## How to run it

```bash
pip install -e ".[dev]"           # or .venv/bin/python -m pip install -e .
jargon-simplifier samples/lease-notice.txt            # offline, neutral tone
jargon-simplifier samples/lease-notice.txt -t legal -r grade-6
jargon-simplifier samples/lease-notice.txt -t medical -f plain
jargon-simplifier letter.txt --llm                    # optional pass, Ollama default
jargon-simplifier letter.txt --llm --url http://localhost:8080/v1 --model qwen2.5
jargon-simplifier notice.txt -o out.txt --overwrite   # only flag that clobbers
```

## Verification results

Run in this folder (Python 3.13, venv):

- `pip install -e .` - installs cleanly; console script `jargon-simplifier`
  and `python -m jargon_simplifier` both work.
- `pytest` - **31 passed** (all offline; the endpoint layer is fully mocked).
- CLI smoke tests - side-by-side, unified and plain formats render; legal
  and medical parenthetical modes work; `--llm` against an unreachable URL
  (port 1) correctly falls back to the offline engine with the
  `fell back to offline engine` note; `-o` refuses to clobber without
  `--overwrite`; `--write` rewrites the input in place; `--offline` never
  touches the network.
- Manual check: `LICENSE` carries the exact line
  `Copyright (c) 2026 Asdale Dynamics, LLC`; README credits
  Asdale Dynamics, LLC; no secrets, keys, or personal data anywhere.

## Known gaps

- Offline swap output is mechanical, not a language model: some word-level
  swaps read awkwardly in unusual grammatical contexts (articles and
  inflections cannot be reasoned about offline; a few double-word collapses
  like "the the" are special-cased).
- The grade-6 sentence splitter only cuts on `;`, `, and`, `, or`,
  `, but`, and `, and then` - sentences long enough to need a split but
  without those joints are left alone.
- The LLM pass trusts the endpoint's completion after basic hygiene checks
  (empty/refusal detection); it does not run a second model to verify
  no-additions compliance.
- `--write` rewrites the input file with no backup copy; it is intentionally
  opt-in-only, but a future `--backup` flag would be more forgiving.
- No auto-update of the glossary; new jargon requires manual entries.
