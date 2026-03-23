"""Core R&D Career English Mentor logic."""

from __future__ import annotations

import os
from typing import Generator, Optional

from .prompt import SYSTEM_PROMPT

try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


class RDEnglishMentor:
    """An AI-powered R&D Career English Mentor.

    Helps Chinese engineers communicate more fluently in English during
    Stand-ups, Design Reviews, Code Reviews, and Technical Discussions.

    Usage::

        mentor = RDEnglishMentor(api_key="sk-...")
        response = mentor.coach("这个功能因为底层 API 不稳定，所以还没上线")
        print(response)

    Parameters
    ----------
    api_key:
        OpenAI API key. Falls back to the ``OPENAI_API_KEY`` environment
        variable when not provided explicitly.
    model:
        OpenAI chat model to use. Defaults to ``"gpt-4o"``.
    base_url:
        Optional custom base URL for OpenAI-compatible APIs.
    """

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: Optional[str] = None,
    ) -> None:
        if not _OPENAI_AVAILABLE:
            raise ImportError(
                "The 'openai' package is required. "
                "Install it with: pip install openai"
            )

        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "An OpenAI API key must be provided either via the "
                "'api_key' parameter or the 'OPENAI_API_KEY' environment variable."
            )

        client_kwargs: dict = {"api_key": resolved_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = openai.OpenAI(**client_kwargs)
        self._model = model
        self._history: list[dict[str, str]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def coach(self, user_input: str) -> str:
        """Send a user message and return the mentor's full response.

        Parameters
        ----------
        user_input:
            A sentence or phrase the user wants to learn how to express
            naturally in English. May be in Chinese or English.

        Returns
        -------
        str
            The structured mentor response containing all four required
            sections: 【地道表达】, 【关键术语】, 【避坑指南】, 【实战练习】.
        """
        self._history.append({"role": "user", "content": user_input})
        messages = self._build_messages()

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
        )

        reply = response.choices[0].message.content or ""
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def stream_coach(self, user_input: str) -> Generator[str, None, None]:
        """Like :meth:`coach` but yields the reply token by token.

        Useful for interactive CLI sessions where showing incremental
        output improves perceived responsiveness.

        Parameters
        ----------
        user_input:
            The user's message (Chinese or English).

        Yields
        ------
        str
            Successive chunks of the mentor's response.
        """
        self._history.append({"role": "user", "content": user_input})
        messages = self._build_messages()

        full_reply: list[str] = []
        with self._client.chat.completions.stream(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_reply.append(delta)
                    yield delta

        self._history.append({"role": "assistant", "content": "".join(full_reply)})

    def reset(self) -> None:
        """Clear the conversation history to start a fresh session."""
        self._history.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_messages(self) -> list[dict[str, str]]:
        """Build the messages list including the system prompt."""
        return [{"role": "system", "content": SYSTEM_PROMPT}] + self._history
