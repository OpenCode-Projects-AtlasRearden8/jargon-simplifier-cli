"""Optional LLM pass against any OpenAI-compatible endpoint.

Defaults to a local Ollama server (``http://localhost:11434/v1``). The client
is configured by base URL only - never by API key - because the tool is meant
to run against local servers. The OpenAI SDK requires a key field, so a
placeholder value is sent; no real credential is ever read, stored, or sent.

If the endpoint is unreachable, times out, or returns an empty or
	evidently-refusal response, the caller falls back to the offline engine
according to the rules in :func:`rewrite`.
"""

from __future__ import annotations

import os

SYSTEM_PROMPT = (
	"You rewrite text into plain English.\n"
	"STRICT NO-ADDITIONS RULES:\n"
	"- You may ONLY use information that is already in the input text.\n"
	"- Never add facts, examples, names, numbers, dates, advice, or opinions.\n"
	"- Never answer, explain, apologize, or greet. Never use markdown or bullets.\n"
	"- Reply with ONLY the rewritten text: no preamble, no quotes, no trailing notes.\n"
	"- Keep every fact, name, number, date, and condition from the original.\n"
	"- Replace jargon with plain English words, and keep sentences short and direct.\n"
	"- Do not use exclamation marks."
)

_REFUSAL_MARKERS = (
	"i cannot", "i can't", "as an ai", "i'm sorry", "i am sorry",
	"here is", "sure!", "certainly",
)


def default_base_url() -> str:
	return os.environ.get("JARGON_BASE_URL", "http://localhost:11434/v1")


def default_model() -> str:
	return os.environ.get("JARGON_MODEL", "llama3.2")


def build_user_prompt(
	text: str,
	tone: str = "neutral",
	reading_level: str = "grade-8",
) -> str:
	tone_hints = {
		"neutral": "Use a neutral, professional plain-English register.",
		"friend": "Write as a friend would: warm, plain, never condescending.",
		"legal": (
			"Aim at a legal-admin audience: plain English, but keep the "
			"original legal terms in parentheses on first use so the record "
			"stays precise."
		),
		"medical": (
			"Aim at a medical-admin audience: plain English, but keep the "
			"original medical terms in parentheses on first use so the record "
			"stays precise."
		),
	}[tone]

	level_hints = {
		"grade-6": "Target a grade-6 reading level: very short sentences, everyday words.",
		"grade-8": "Target a grade-8 reading level: short sentences, simple words.",
		"grade-12": "Target a grade-12 reading level: clear and direct, but naturally written.",
	}[reading_level]

	return (
		f"{tone_hints} {level_hints}\n"
		"Rewrite the following text under the strict no-additions rules.\n"
		"\n<text>\n"
		f"{text}\n"
		"</text>"
	)


def llm_rewrite(
	text: str,
	tone: str = "neutral",
	reading_level: str = "grade-8",
	base_url: str | None = None,
	model: str | None = None,
	timeout: float = 60.0,
) -> str:
	"""Return the LLM's plain-English rewrite, or raise to signal fallback."""

	import openai

	base_url = base_url or default_base_url()
	model = model or default_model()

	client = openai.OpenAI(
		base_url=base_url,
		api_key="not-required-for-local-endpoints",
		timeout=timeout,
	)

	response = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": build_user_prompt(text, tone, reading_level)},
		],
		temperature=0.0,
	)

	content = response.choices[0].message.content if response.choices else None
	return _clean(content)


def _clean(content: str | None) -> str:
	if not content:
		raise RuntimeError("endpoint returned an empty completion")
	out = content.strip()
	# Strip one decorative wrapper without touching the content itself.
	if len(out) >= 2 and out[0] == out[-1] and out[0] in "\"'`":
		out = out[1:-1].strip()
	for marker in _REFUSAL_MARKERS:
		if out[: len(marker)].lower() == marker:
			raise RuntimeError(f"endpoint refused the rewrite ({marker!r})")
	if not out:
		raise RuntimeError("endpoint returned a blank completion")
	return out


def rewrite(
	text: str,
	tone: str = "neutral",
	reading_level: str = "grade-8",
	base_url: str | None = None,
	model: str | None = None,
	timeout: float = 60.0,
	offline: bool = False,
):
	"""Rewrite with the LLM pass, falling back to the offline engine.

	Fallback rules (both prompted and automatic ``--offline``):

	1. connection errors or timeouts when contacting the endpoint,
	2. empty, blank, quoted-only, or refusal-style completions,
	3. any unexpected SDK error.

	The returned :class:`jargon_simplifier.engine.RewriteResult` says which
	engine produced the text.
	"""

	from . import engine

	if offline:
		return engine.rewrite_offline(text, tone, reading_level)

	try:
		plain = llm_rewrite(
			text, tone=tone, reading_level=reading_level,
			base_url=base_url, model=model, timeout=timeout,
		)
	except Exception as exc:  # noqa: BLE001 - any endpoint failure falls back
		result = engine.rewrite_offline(text, tone, reading_level)
		result.note = f"fell back to offline engine: {exc}"
		return result

	# Enrich the glossary: keep engine swaps the LLM actually applied, and flag
	# glossary terms that disappeared from the output.
	from .engine import Edit, RewriteResult

	edits: dict[str, Edit] = {}
	lower_out = plain.lower()
	for term in sorted(engine.GLOSSARY, key=len, reverse=True):
		swap, definition = engine.GLOSSARY[term]
		matches = engine._matches(term, text)
		if not matches:
			continue
		if term.lower() not in lower_out:
			edits[term] = Edit(
				term=term, plain=swap or "(removed)", definition=definition,
				count=len(matches), domain=engine._domain_of(term),
			)

	return RewriteResult(
		original=text,
		plain=plain,
		tone=tone,
		reading_level=reading_level,
		source=f"llm ({base_url or default_base_url()}; model={model or default_model()})",
		note="llm pass with strict no-additions prompt",
		edits=sorted(edits.values(), key=lambda e: e.term.lower()),
	)


def llm_default_url() -> str:
	return default_base_url()
