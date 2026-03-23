"""OpenAI-backed mentor session."""

from __future__ import annotations

from typing import Iterator, Optional

from .core import MentorResponse, build_user_message, parse_response
from .prompt import SYSTEM_PROMPT


class MentorSession:
    """Maintain a conversation with the R&D Career English Mentor.

    Parameters
    ----------
    api_key:
        OpenAI API key.  If *None* the value of the ``OPENAI_API_KEY``
        environment variable is used (standard OpenAI SDK behaviour).
    model:
        Chat-completion model to use.  Defaults to ``gpt-4o``.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
    ) -> None:
        try:
            from openai import OpenAI  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required to use MentorSession. "
                "Install it with: pip install openai"
            ) from exc

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._history: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ask(self, user_input: str) -> MentorResponse:
        """Send *user_input* to the mentor and return a structured response."""
        message = build_user_message(user_input)
        self._history.append({"role": "user", "content": message})

        completion = self._client.chat.completions.create(
            model=self._model,
            messages=self._history,  # type: ignore[arg-type]
        )

        raw = completion.choices[0].message.content or ""
        self._history.append({"role": "assistant", "content": raw})
        return parse_response(raw)

    def stream(self, user_input: str) -> Iterator[str]:
        """Yield response text chunks as they arrive from the API.

        The full accumulated response is stored in conversation history
        once streaming is complete.
        """
        message = build_user_message(user_input)
        self._history.append({"role": "user", "content": message})

        stream = self._client.chat.completions.create(
            model=self._model,
            messages=self._history,  # type: ignore[arg-type]
            stream=True,
        )

        full_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            yield delta

        self._history.append({"role": "assistant", "content": full_response})

    def reset(self) -> None:
        """Clear conversation history (keeps the system prompt)."""
        self._history = [self._history[0]]
