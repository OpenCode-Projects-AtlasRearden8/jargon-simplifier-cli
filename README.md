# jargon-simplifier

Rewrite stiff prose into plain English from the command line. Pick a reading
level and a lean (legal, medical-admin) or friend tone; get a side-by-side
diff plus a glossary of every term that was swapped. The LLM pass - if you
opt into one - is governed by a strict no-additions prompt, so nothing is
invented.

Built and maintained by **Asdale Dynamics, LLC**. Part of the same
beginner-friendly, local-first family as Dylan Asdale's work explaining AI
"like a friend would" at [dylanasdale.github.io](https://dylanasdale.github.io)
and in *The Massive AI Manual*.

Works two ways:

- **Offline (default):** a built-in, hand-maintained jargon glossary does
  word-level swaps. No network, no model, no data leaves your machine.
- **Optional LLM pass** (`--llm`): sends the text to any OpenAI-compatible
  endpoint - default is a local Ollama server at `localhost:11434/v1` -
  with a strict no-additions system prompt. If the endpoint is unreachable,
  times out, or misbehaves, the tool falls back to the offline engine and
  tells you it did. The endpoint is configured by base URL only; the tool
  never asks for, reads, or stores an API key.

Nothing is written back to disk unless you pass an explicit flag
(`--write` for in-place, `-o` with `--overwrite` to clobber a target).

## Install and run

Requires Python 3.9+. From a checkout of this folder:

```bash
pip install .                  # or: pip install -e ".[dev]"
jargon-simplifier samples/letter.txt
```

Or without installing anything:

```bash
python -m jargon_simplifier samples/letter.txt
```

## The tone and reading-level dials

```bash
# Friendly voice for a client letter
jargon-simplifier letter.txt -t friend

# Legal lean: plainer wording, but keeps the legal term in parentheses
# on first use so the record stays precise
jargon-simplifier lease-notice.txt -t legal

# Medical-admin lean, at a grade-6 reading level (long sentences are
# split at existing punctuation; no words are added)
jargon-simplifier bill-letter.txt -t medical -r grade-6

# Clean text file of just the rewrite, no diff
jargon-simplifier notice.txt -f plain
```

Tones: `neutral` (default), `friend`, `legal`, `medical`.
Reading levels: `grade-6`, `grade-8` (default), `grade-12`.
Formats: `side-by-side` (default), `unified`, `plain`.

## Using an LLM endpoint (optional)

```bash
# Ollama running locally (the default endpoint and model)
ollama pull llama3.2
jargon-simplifier letter.txt --llm

# Any other OpenAI-compatible server - by base URL, never a key
jargon-simplifier letter.txt --llm --url http://localhost:8080/v1 --model qwen2.5

jargon-simplifier letter.txt --llm --timeout 90    # be patient with big models
```

Environment variables: `JARGON_BASE_URL`, `JARGON_MODEL`.

The system prompt forbids adding facts, examples, numbers, advice,
greetings, or markdown, and the tool still falls back to the offline
glossary engine if a completion comes back empty or refusal-shaped.

## Safety rails

- **No additions:** the LLM pass ships behind a strict no-additions prompt;
  offline swaps only reword what is already there.
- **No overwrite without an explicit flag:** output goes to stdout unless
  you pass `--write` (in place) or `-o` plus `--overwrite` for clobbering.
- **No keys, ever:** endpoint configured by `--url` / `JARGON_BASE_URL`
  only. Nothing about this tool collects or transmits credentials.
- **Local first:** offline mode never touches the network.

## Fallback rules

With `--llm`, these conditions drop you to the offline engine, and the
report's `Note:` line says so:

1. the endpoint is unreachable or the request times out,
2. no choices / empty or blank completion comes back,
3. an SDK error of any kind.

Use `--offline` to skip the network entirely.

## Glossary of swapped terms

Every run prints a glossary of each term that was removed, its plain-swap
wording, a short definition, the domain it came from (legal,
medical-admin, general, phrasing), and how many times it was swapped. With
`--llm`, terms the model conspicuously dropped are included with their
definitions so you can check the wording against the source.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

All tests run fully offline; the LLM pass is exercised through a mocked
endpoint (bad completions, timeouts, refusals, and clean passes).

## Project layout

```
jargon_simplifier/
  glossary.py   built-in jargon -> plain-English swaps (+ definitions)
  engine.py     offline rule-based rewriter (swap, parentheticals, sentence splits)
  llm.py        optional OpenAI-compatible pass + fallback rules
  reporting.py  side-by-side / unified diff and the swapped-terms glossary
  cli.py        argparse command line interface
tests/          pytest suite (mocked endpoint, offline everything else)
samples/        sample inputs to try
```

## License

MIT - see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.

This tool explains and rewrites text; it is educational software and is not
legal or medical advice.
