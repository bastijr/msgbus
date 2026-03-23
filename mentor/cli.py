"""Command-line interface for the R&D Career English Mentor."""

from __future__ import annotations

import argparse
import os
import sys

from .mentor import RDEnglishMentor


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rd-mentor",
        description=(
            "🤖 R&D Career English Mentor — helps Chinese engineers express "
            "themselves naturally during Stand-ups, Design Reviews, Code Reviews, "
            "and Technical Discussions."
        ),
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=(
            "OpenAI API key. Defaults to the OPENAI_API_KEY environment variable."
        ),
    )
    parser.add_argument(
        "--model",
        default=RDEnglishMentor.DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {RDEnglishMentor.DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL for OpenAI-compatible APIs (optional).",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help=(
            "Sentence or phrase to coach (Chinese or English). "
            "If omitted, the program enters interactive mode."
        ),
    )
    return parser


def _print_banner() -> None:
    banner = (
        "\n"
        "╔══════════════════════════════════════════════════════╗\n"
        "║  🤖  R&D Career English Mentor  研发职场英语导师      ║\n"
        "║  Type a sentence you want to express in English.     ║\n"
        "║  Type 'quit' or 'exit' to leave. 'reset' to restart. ║\n"
        "╚══════════════════════════════════════════════════════╝\n"
    )
    print(banner)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        mentor = RDEnglishMentor(
            api_key=args.api_key,
            model=args.model,
            base_url=args.base_url,
        )
    except (ImportError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Single-shot mode
    if args.input:
        try:
            reply = mentor.coach(args.input)
            print(reply)
        except Exception as exc:  # noqa: BLE001
            print(f"Error calling the API: {exc}", file=sys.stderr)
            return 1
        return 0

    # Interactive mode
    _print_banner()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! 再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye! 再见！")
            break
        if user_input.lower() == "reset":
            mentor.reset()
            print("Conversation history cleared. 对话历史已清除。\n")
            continue

        print()
        try:
            for chunk in mentor.stream_coach(user_input):
                print(chunk, end="", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"\nError calling the API: {exc}", file=sys.stderr)
        print("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
