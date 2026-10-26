"""Output formatting: side-by-side (or unified) diff plus glossary of swaps."""

from __future__ import annotations

import difflib
import os
import shutil
import textwrap

_LABEL_ORIGINAL = "ORIGINAL"
_LABEL_PLAIN = "PLAIN ENGLISH"


def _terminal_width() -> int:
    try:
        raw = os.environ.get("COLUMNS")
        if raw:
            return int(raw)
    except (TypeError, ValueError):
        pass
    return shutil.get_terminal_size((80, 24)).columns


def _wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            lines.append("")
            continue
        lines.extend(
            textwrap.wrap(
                line, width=width, break_long_words=False, break_on_hyphens=False
            )
            or [""]
        )
    return lines or [""]


def side_by_side(
    left: str,
    right: str,
    total_width: int | None = None,
    label_left: str = _LABEL_ORIGINAL,
    label_right: str = _LABEL_PLAIN,
) -> str:
    """Render a two-column diff. Markers: ' ' equal, ':' changed, '-' / '+'."""

    width = max(total_width or _terminal_width(), 40)
    gutter = 4
    col = max((width - gutter) // 2, 15)

    left_lines = _wrap(left, col)
    right_lines = _wrap(right, col)
    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

    rows: list[tuple[str, str, str]] = []

    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(a1 - a0):
                rows.append((" ", left_lines[a0 + k], right_lines[b0 + k]))
        elif tag == "delete":
            for line in left_lines[a0:a1]:
                rows.append(("-", line, ""))
        elif tag == "insert":
            for line in right_lines[b0:b1]:
                rows.append(("+", "", line))
        elif tag == "replace":
            for line in left_lines[a0:a1]:
                rows.append(("-", line, ""))
            for line in right_lines[b0:b1]:
                rows.append(("+", "", line))

    header = [f"{label_left:<{col}}{gutter * ' '}{label_right:<{col}}"]
    header.append(f"{'-' * (col - 2):<{col}}{gutter * ' '}{'-' * (col - 2):<{col}}")

    out = header
    for marker, show_l, show_r in rows:
        l = show_l if marker in (" ", "-") else ""
        r = show_r if marker in (" ", "+") else ""
        out.append(f"{l:<{col}}{gutter * ' '}{r:<{col}}")
    return "\n".join(out)


def unified(left: str, right: str, label_left: str = _LABEL_ORIGINAL,
            label_right: str = _LABEL_PLAIN) -> str:
    return "\n".join(
        difflib.unified_diff(
            left.splitlines(), right.splitlines(),
            fromfile=label_left, tofile=label_right, lineterm="",
        )
    )


def glossary_table(edits) -> str:
    """Render the glossary of terms that were swapped out."""

    if not edits:
        return "Glossary (swapped terms): none found."

    width = max(_terminal_width(), 72)
    lines = [f"Glossary: {len(edits)} term{'s' if len(edits) != 1 else ''} swapped", "=" * width]
    for edit in edits:
        head = f"{edit.term} -> {edit.plain if edit.plain else '(removed)'}"
        if edit.count > 1:
            head += f"  (x{edit.count})"
        meta = f"   [{edit.domain}]"
        if len(head) + len(meta) <= width:
            head = head + meta
        else:
            head = head + "\n" + meta
        lines.append(head)
        lines.append(textwrap.fill(edit.definition, width=width,
                                   initial_indent="    - ", subsequent_indent="    "))
    return "\n".join(lines)


def render_report(result, style: str = "side-by-side") -> str:
    """Full CLI report: header, diff, glossary."""
    parts: list[str] = []

    header = [
        f"Source: {result.source}",
        f"Tone: {result.tone} | Reading level: {result.reading_level}",
    ]
    if result.note:
        header.append(f"Note: {result.note}")
    parts.append("\n".join(header))

    if style == "unified":
        parts.append(
            unified(result.original, result.plain)
        )
    elif style == "plain":
        parts.append(f"{_LABEL_PLAIN}\n{'=' * len(_LABEL_PLAIN)}\n{result.plain}")
    else:
        parts.append(side_by_side(result.original, result.plain))

    if style != "plain":
        parts.append(glossary_table(result.edits))

    return "\n\n".join(parts) + "\n"
