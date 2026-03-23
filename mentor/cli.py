"""Command-line interface for the R&D Career English Mentor."""

from __future__ import annotations

import argparse
import os
import sys


def _print_banner() -> None:
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════╗\n"
        "║   🤖  R&D Career English Mentor  研发职场英语导师         ║\n"
        "║   Type your Chinese expression or English draft.         ║\n"
        "║   Commands: 'reset' | 'quit' / 'exit'                   ║\n"
        "╚══════════════════════════════════════════════════════════╝\n"
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mentor",
        description=(
            "R&D Career English Mentor — helps Chinese-speaking engineers "
            "communicate more naturally in Stand-ups, Design Reviews, "
            "Code Reviews, and Technical Discussions."
        ),
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI chat model to use (default: gpt-4o).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=(
            "OpenAI API key. Defaults to the OPENAI_API_KEY "
            "environment variable."
        ),
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output and wait for the full response.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry-point for the ``mentor`` CLI command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    api_key: str | None = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "Error: No OpenAI API key found. "
            "Set the OPENAI_API_KEY environment variable or use --api-key.",
            file=sys.stderr,
        )
        return 1

    from .session import MentorSession  # imported here to surface ImportError cleanly

    session = MentorSession(api_key=api_key, model=args.model)

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
            session.reset()
            print("[Session reset — conversation history cleared.]\n")
            continue

        print("\nMentor:\n")
        if args.no_stream:
            response = session.ask(user_input)
            print(response.format())
        else:
            for chunk in session.stream(user_input):
                print(chunk, end="", flush=True)
            print()  # newline after streaming finishes
        print()

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
