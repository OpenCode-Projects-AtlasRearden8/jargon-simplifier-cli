"""The ``jargon-simplifier`` command line interface."""

from __future__ import annotations

import argparse
import os
import sys

from . import engine, llm, reporting

EPILOG = (
	"Endpoint is configured by base URL only - never by an API key. "
	"Environment variables: JARGON_BASE_URL, JARGON_MODEL."
)


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="jargon-simplifier",
		description=(
			"Rewrite stiff prose into plain English: pick a tone, get a "
			"side-by-side diff plus a glossary of every swapped term. "
			"Offline by default; pass --llm to use a local OpenAI-compatible endpoint."
		),
		epilog=EPILOG,
	)
	parser.add_argument(
		"input", metavar="PATH", nargs="?", default="-",
		help="input text file ('-' or nothing to read stdin)",
	)
	parser.add_argument(
		"-t", "--tone", choices=list(engine.TONES), default="neutral",
		metavar="TONE",
		help="neutral | friend | legal | medical (default: neutral)",
	)
	parser.add_argument(
		"-r", "--reading-level", choices=list(engine.READING_LEVELS),
		default="grade-8", metavar="LEVEL",
		help="grade-6 | grade-8 | grade-12 (default: grade-8)",
	)
	parser.add_argument(
		"-f", "--format", choices=("side-by-side", "unified", "plain"),
		default="side-by-side", dest="fmt", metavar="FORMAT",
		help="diff style (default: side-by-side)",
	)
	parser.add_argument(
		"-o", "--output", metavar="PATH", default=None,
		help="write the plain-English text to PATH (refuses to clobber "
			 "an existing file without --overwrite)",
	)
	parser.add_argument(
		"--write", action="store_true",
		help="overwrite the input file in place with the rewrite "
			 "(explicit flag required, does nothing when reading stdin)",
	)
	parser.add_argument(
		"--overwrite", action="store_true",
		help="allow -o/--output to replace an existing file",
	)
	parser.add_argument(
		"--llm", action="store_true",
		help="run an OpenAI-compatible endpoint pass; falls back to the "
			 "offline engine if the endpoint is unreachable or misbehaves",
	)
	parser.add_argument(
		"--offline", action="store_true",
		help="force the offline glossary engine (no network at all)",
	)
	parser.add_argument(
		"--url", default=None, metavar="BASE_URL",
		help=f"endpoint base URL (default: {llm.default_base_url()})",
	)
	parser.add_argument(
		"--model", default=None, metavar="NAME",
		help=f"model name at the endpoint (default: {llm.default_model()})",
	)
	parser.add_argument(
		"--timeout", type=float, default=60.0,
		metavar="SECONDS",
		help="endpoint request timeout (default: 60)",
	)
	return parser


def read_input(path: str) -> str:
	if path == "-":
		if sys.stdin.isatty():
			raise SystemExit("no input: give a PATH or pipe text in (see --help)")
		return sys.stdin.read()
	with open(path, "r", encoding="utf-8") as handle:
		return handle.read()


def write_output(result, args):
	if args.write and args.input in ("-", None):
		raise SystemExit("--write needs an input PATH file (stdin cannot be overwritten)")
	if args.output:
		if os.path.exists(args.output) and not args.overwrite:
			raise SystemExit(
				f"refusing to overwrite {args.output}: pass --overwrite to allow"
			)
		with open(args.output, "w", encoding="utf-8") as handle:
			handle.write(result.plain)
	if args.write:
		with open(args.input, "w", encoding="utf-8") as handle:
			handle.write(result.plain)


def main(argv: list[str] | None = None) -> int:
	args = build_parser().parse_args(argv)
	if args.offline:
		args.llm = False

	text = read_input(args.input)
	if not text.strip():
		raise SystemExit("input is empty; nothing to rewrite")

	result = llm.rewrite(
		text,
		tone=args.tone,
		reading_level=args.reading_level,
		base_url=args.url,
		model=args.model,
		timeout=args.timeout,
		offline=args.offline or not args.llm,
	)

	report = reporting.render_report(result, style=args.fmt)
	print(report, end="")

	if args.output or args.write:
		write_output(result, args)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
