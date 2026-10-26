"""Offline rewrite engine: whole-phrase jargon swaps, no network, no invention.

Two levers, both mechanical:

* Tone - which glossary swaps get applied and how they are shown (the legal
  tone keeps the original term in parentheses on first use, so the record
  stays precise; the medical tone does the same for medical-admin terms).
* Reading level - at ``grade-6`` long sentences are split at semicolons and
  "X, and Y" joints. Sentence splitting reuses words already in the sentence;
  nothing new is written.

Every swap is logged as an :class:`Edit` so the caller can build the glossary
of swapped terms.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .glossary import GLOSSARY, LEGAL_TERMS, MEDICAL_TERMS

TONES = ("neutral", "friend", "legal", "medical")
READING_LEVELS = ("grade-6", "grade-8", "grade-12")

_MAX_WORDS_FOR_SPLIT = 26


@dataclass
class Edit:
    """One glossary entry that was actually applied."""

    term: str
    plain: str
    definition: str
    count: int
    domain: str = "general"  # general | legal | medical-admin | phrasing


@dataclass
class RewriteResult:
    original: str
    plain: str
    tone: str
    reading_level: str
    source: str
    note: str
    edits: list


def _swap_case(matched: str, swap: str) -> str:
    if not swap or not swap[0].isalpha():
        return swap
    if matched[:1].isupper():
        return swap[:1].upper() + swap[1:]
    return swap


def _matches(term: str, text: str) -> list[re.Match]:
    return list(re.finditer(r"\b" + re.escape(term) + r"\b", text, re.IGNORECASE))


def _domain_of(term: str) -> str:
    if term in LEGAL_TERMS:
        return "legal"
    if term in MEDICAL_TERMS:
        return "medical-admin"
    if term[0].isupper():
        return "phrasing"
    return "general"


def rewrite_offline(
    text: str, tone: str = "neutral", reading_level: str = "grade-8"
) -> RewriteResult:
    """Rewrite ``text`` using only built-in glossary swaps."""

    if tone not in TONES:
        raise ValueError(f"unknown tone: {tone!r}")
    if reading_level not in READING_LEVELS:
        raise ValueError(f"unknown reading level: {reading_level!r}")

    edits: dict[str, Edit] = {}
    out = text

    # Longest terms first so e.g. "please be advised that" is matched whole.
    for term in sorted(GLOSSARY, key=len, reverse=True):
        swap, definition = GLOSSARY[term]

        paren_keep = (
            (tone == "legal" and _domain_of(term) == "legal")
            or (tone == "medical" and _domain_of(term) == "medical-admin")
        )

        matches = _matches(term, out)
        if not matches:
            continue

        count = len(matches)
        plain_shown = swap

        # Apply replacements right-to-left so indices stay valid. The
        # leftmost occurrence keeps the original term in parentheses.
        for i, match in enumerate(reversed(matches)):
            start, end = match.span()
            replacement = _swap_case(match.group(0), swap)
            if paren_keep and swap and i == len(matches) - 1:
                replacement = f"{replacement} ({term})"
            out = out[:start] + replacement + out[end:]

        entry = edits.get(term)
        if entry is None:
            entry = Edit(
                term=term,
                plain=plain_shown,
                definition=definition,
                count=count,
                domain=_domain_of(term),
            )
            edits[term] = entry
        else:
            entry.count += count

    before = out
    out = _cleanup(out)
    if out != before:
        edits["debris-cleanup"] = Edit(
            term="cleanup (spacing and punctuation)",
            plain="",
            definition=(
                "Whitespace and punctuation debris left by removals was "
                "tidied: collapsed double spaces, stray leading commas, and "
                "sentence-start capitalization. No words were added."
            ),
            count=1,
            domain="phrasing",
        )

    if reading_level == "grade-6":
        before = out
        out = split_long_sentences(out)
        if out != before:
            edits["sentence-splitting"] = Edit(
                term="sentence-splitting",
                plain="(long sentences split at existing punctuation)",
                definition=(
                    "Sentences longer than %d words were split at existing "
                    "punctuation. No words were added." % _MAX_WORDS_FOR_SPLIT
                ),
                count=1,
                domain="phrasing",
            )

    return RewriteResult(
        original=text,
        plain=out,
        tone=tone,
        reading_level=reading_level,
        source="offline",
        note="offline mode: rule-based glossary swaps only",
        edits=sorted(edits.values(), key=lambda e: e.term.lower()),
    )


# --------------------------------------------------------------- sentences

def _cleanup(text: str) -> str:
    """Tidy spacing/punctuation debris left by (removed) phrases.

    Collapses double spaces and stray leading commas/semicolons, and
    capitalizes sentence starts. Words are never added.
    """

    out = re.sub(r"[ \t]{2,}", " ", text)
    out = re.sub(r"(?m)^[ \t]*[;,.] ?", "", out)
    out = re.sub(r"[ \t]+([,.;:!?])", r"\1", out)
    out = re.sub(r"\bthe the\b", "the", out, flags=re.IGNORECASE)
    out = re.sub(r"\ba a\b", "a", out, flags=re.IGNORECASE)
    out = re.sub(r"\ban an\b", "an", out, flags=re.IGNORECASE)

    chars: list[str] = []
    at_sentence_start = True
    for ch in out:
        if at_sentence_start and ch.isalpha():
            chars.append(ch.upper())
            at_sentence_start = False
            continue
        chars.append(ch)
        if ch in ".!?" and not chars[-2:-1] or True:
            pass
        if ch in ".!?":
            at_sentence_start = True
        elif not ch.isspace():
            at_sentence_start = False
    if at_sentence_start and chars and chars[-1].isspace():
        pass
    return "".join(chars)


def _split_sentences(text: str):
    return _SENTENCE_BOUNDARY.split(text)


def split_long_sentences(text: str, max_words: int = _MAX_WORDS_FOR_SPLIT) -> str:
    """Split long sentences at existing semicolons / comma-conjunctions.

    Purely mechanical: the words and grammar of the original sentence are
    preserved as-is; only the joiner punctuation changes and the following
    word is capitalized.
    """

    fixed: list[str] = []
    for sentence in _split_sentences(text):
        if _word_count(sentence) <= max_words:
            fixed.append(sentence)
            continue

        pieces = [sentence]
        changed = True
        while changed:
            changed = False
            requeue: list[str] = []
            for piece in pieces:
                if _word_count(piece) <= max_words:
                    requeue.append(piece)
                    continue
                cut = _find_split_point(piece)
                if cut is None:
                    requeue.append(piece)
                    continue
                left, right = cut
                requeue.append(left)
                requeue.append(right)
                changed = True
            pieces = requeue

        fixed.append(" ".join(pieces))
    return " ".join(fixed)


def _find_split_point(sentence: str):
    for joiner in _JOINERS:
        mid = sentence.find(joiner)
        if 0 < mid < len(sentence) - len(joiner):
            left = sentence[:mid].rstrip()
            right = sentence[mid + len(joiner):].lstrip()
            if right and _word_count(left) >= 3 and _word_count(right) >= 3:
                right = right[0].upper() + right[1:]
                if not left.endswith((".", "!", "?", ":", ";")):
                    left = left.rstrip(",") + "."
                return left, right
    return None

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

_JOINERS = ("; ", ", and ", ", or ", ", and then ", ", but ")


def _word_count(text: str) -> int:
    return len(text.split())
