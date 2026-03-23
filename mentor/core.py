"""Core mentor logic: response formatting and output structure."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


SECTION_HEADERS = {
    "natural_way": "【地道表达】 (The Natural Way)",
    "key_terms": "【关键术语】 (Key Tech Terms)",
    "pitfalls": "【避坑指南】 (Common Pitfalls)",
    "practice": "【实战练习】 (Practice)",
}


@dataclass
class MentorResponse:
    """Structured response from the R&D Career English Mentor."""

    natural_way: str = ""
    key_terms: str = ""
    pitfalls: str = ""
    practice: str = ""
    raw: str = ""

    def format(self) -> str:
        """Return a formatted string with all four required sections."""
        parts = []
        for key, header in SECTION_HEADERS.items():
            content = getattr(self, key).strip()
            parts.append(f"**{header}**\n{content}")
        return "\n\n".join(parts)

    def __str__(self) -> str:  # pragma: no cover
        return self.format()


def parse_response(raw: str) -> MentorResponse:
    """Parse an LLM response into a structured :class:`MentorResponse`.

    The parser is lenient: it accepts both the Chinese section headers
    (``【地道表达】``, ``【关键术语】``, etc.) and the parenthetical English
    equivalents, with or without surrounding ``**`` markdown markers.
    """
    header_patterns = {
        "natural_way": r"【地道表达】",
        "key_terms": r"【关键术语】",
        "pitfalls": r"【避坑指南】",
        "practice": r"【实战练习】",
    }

    # Build a combined pattern that matches any section header so we can split.
    combined = "|".join(
        rf"(?:\*{{0,2}}{pat}[^\n]*\*{{0,2}})"
        for pat in header_patterns.values()
    )
    splitter = re.compile(combined)

    sections: dict[str, str] = {}
    last_key: Optional[str] = None
    last_end = 0

    for match in splitter.finditer(raw):
        if last_key is not None:
            sections[last_key] = raw[last_end : match.start()].strip()
        for key, pat in header_patterns.items():
            if re.search(pat, match.group()):
                last_key = key
                break
        last_end = match.end()

    if last_key is not None:
        sections[last_key] = raw[last_end:].strip()

    return MentorResponse(
        natural_way=sections.get("natural_way", ""),
        key_terms=sections.get("key_terms", ""),
        pitfalls=sections.get("pitfalls", ""),
        practice=sections.get("practice", ""),
        raw=raw,
    )


def build_user_message(user_input: str) -> str:
    """Wrap the user's raw input in a brief framing message."""
    return (
        f"Please help me express the following in natural R&D English:\n\n"
        f"{user_input}\n\n"
        f"Respond with all four required sections: "
        f"【地道表达】, 【关键术语】, 【避坑指南】, 【实战练习】."
    )
