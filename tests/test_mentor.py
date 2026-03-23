"""Unit tests for the R&D Career English Mentor package."""

from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_RESPONSE = """\
**【地道表达】 (The Natural Way)**
- "The rollout of this feature is on hold due to the instability of the underlying API."
- "We're holding off on deploying this feature because the underlying API has been unreliable."

**【关键术语】 (Key Tech Terms)**
- **Rollout**: The gradual or phased deployment of a feature or update to production.
- **Underlying**: Refers to the foundational layer (e.g., underlying API, underlying infrastructure).
- **On hold**: Temporarily paused or delayed.

**【避坑指南】 (Common Pitfalls)**
- ❌ "This feature is not online yet." → Sounds unnatural.
- ✅ Use "pushed to production," "deployed," or "rolled out."

**【实战练习】 (Practice)**
Now try this scenario: 这个 PR 因为测试覆盖率不够，所以还没合并。
"""


def _make_openai_stub(content: str = SAMPLE_RESPONSE) -> types.ModuleType:
    """Return a minimal mock of the openai module."""
    openai_mod = types.ModuleType("openai")

    message = MagicMock()
    message.content = content

    choice = MagicMock()
    choice.message = message

    completion = MagicMock()
    completion.choices = [choice]

    client_instance = MagicMock()
    client_instance.chat.completions.create.return_value = completion

    openai_mod.OpenAI = MagicMock(return_value=client_instance)
    return openai_mod


# ---------------------------------------------------------------------------
# Tests for mentor.core
# ---------------------------------------------------------------------------


class TestParseResponse(unittest.TestCase):
    def test_all_four_sections_parsed(self):
        from mentor.core import parse_response

        result = parse_response(SAMPLE_RESPONSE)
        self.assertIn("rollout", result.natural_way.lower())
        self.assertIn("Rollout", result.key_terms)
        self.assertIn("not online", result.pitfalls)
        self.assertIn("PR", result.practice)

    def test_raw_stored(self):
        from mentor.core import parse_response

        result = parse_response(SAMPLE_RESPONSE)
        self.assertEqual(result.raw, SAMPLE_RESPONSE)

    def test_empty_input(self):
        from mentor.core import parse_response

        result = parse_response("")
        self.assertEqual(result.natural_way, "")
        self.assertEqual(result.key_terms, "")
        self.assertEqual(result.pitfalls, "")
        self.assertEqual(result.practice, "")

    def test_partial_response_does_not_crash(self):
        from mentor.core import parse_response

        partial = "**【地道表达】 (The Natural Way)**\nSome expression.\n"
        result = parse_response(partial)
        self.assertIn("Some expression", result.natural_way)

    def test_format_contains_all_headers(self):
        from mentor.core import parse_response

        result = parse_response(SAMPLE_RESPONSE)
        formatted = result.format()
        self.assertIn("【地道表达】", formatted)
        self.assertIn("【关键术语】", formatted)
        self.assertIn("【避坑指南】", formatted)
        self.assertIn("【实战练习】", formatted)


class TestBuildUserMessage(unittest.TestCase):
    def test_includes_original_input(self):
        from mentor.core import build_user_message

        msg = build_user_message("我想说这个功能还没上线")
        self.assertIn("我想说这个功能还没上线", msg)

    def test_includes_section_reminder(self):
        from mentor.core import build_user_message

        msg = build_user_message("test")
        self.assertIn("【地道表达】", msg)


# ---------------------------------------------------------------------------
# Tests for mentor.prompt
# ---------------------------------------------------------------------------


class TestSystemPrompt(unittest.TestCase):
    def test_prompt_contains_key_sections(self):
        from mentor.prompt import SYSTEM_PROMPT

        for keyword in [
            "Terminology Correction",
            "Output Format",
            "【地道表达】",
            "【关键术语】",
            "【避坑指南】",
            "【实战练习】",
        ]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, SYSTEM_PROMPT)

    def test_prompt_not_empty(self):
        from mentor.prompt import SYSTEM_PROMPT

        self.assertGreater(len(SYSTEM_PROMPT), 500)


# ---------------------------------------------------------------------------
# Tests for mentor.session
# ---------------------------------------------------------------------------


class TestMentorSession(unittest.TestCase):
    def setUp(self):
        self._openai_stub = _make_openai_stub()
        sys.modules["openai"] = self._openai_stub

    def tearDown(self):
        sys.modules.pop("openai", None)
        # Remove cached sub-module imports so next test starts fresh.
        for mod in list(sys.modules):
            if mod.startswith("mentor"):
                sys.modules.pop(mod, None)

    def _make_session(self) -> "MentorSession":
        from mentor.session import MentorSession

        return MentorSession(api_key="test-key")

    def test_ask_returns_mentor_response(self):
        from mentor.core import MentorResponse

        session = self._make_session()
        result = session.ask("这个功能因为底层 API 不稳定，所以还没上线")
        self.assertIsInstance(result, MentorResponse)
        self.assertIn("rollout", result.natural_way.lower())

    def test_history_grows_after_ask(self):
        session = self._make_session()
        # System prompt is the first message.
        self.assertEqual(len(session._history), 1)
        session.ask("test input")
        # After one exchange: system + user + assistant = 3
        self.assertEqual(len(session._history), 3)

    def test_reset_clears_history(self):
        session = self._make_session()
        session.ask("test input")
        session.reset()
        # Only the system prompt should remain.
        self.assertEqual(len(session._history), 1)
        self.assertEqual(session._history[0]["role"], "system")

    def test_missing_openai_raises_import_error(self):
        # Temporarily remove the openai stub so the import inside MentorSession fails.
        mentor_mods = {k: v for k, v in sys.modules.items() if k.startswith("mentor")}
        with patch.dict(sys.modules, {"openai": None}, clear=False):
            # Also evict cached mentor modules so MentorSession is re-imported.
            for mod in mentor_mods:
                sys.modules.pop(mod, None)
            from mentor.session import MentorSession

            with self.assertRaises(ImportError):
                MentorSession(api_key="key")
        # Restore mentor modules after the patch context exits.
        sys.modules.update(mentor_mods)


# ---------------------------------------------------------------------------
# Tests for mentor.cli
# ---------------------------------------------------------------------------


class TestCLI(unittest.TestCase):
    def setUp(self):
        self._openai_stub = _make_openai_stub()
        sys.modules["openai"] = self._openai_stub

    def tearDown(self):
        sys.modules.pop("openai", None)
        for mod in list(sys.modules):
            if mod.startswith("mentor"):
                sys.modules.pop(mod, None)

    def test_missing_api_key_returns_1(self):
        # Ensure env var is absent.
        with patch.dict("os.environ", {}, clear=True):
            from mentor.cli import main

            ret = main(["--no-stream"])
        self.assertEqual(ret, 1)

    def test_quit_command_exits_cleanly(self):
        with patch("builtins.input", side_effect=["quit"]):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                from mentor.cli import main

                ret = main(["--no-stream"])
        self.assertEqual(ret, 0)

    def test_eof_exits_cleanly(self):
        with patch("builtins.input", side_effect=EOFError):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                from mentor.cli import main

                ret = main(["--no-stream"])
        self.assertEqual(ret, 0)

    def test_reset_command_resets_session(self):
        inputs = iter(["reset", "quit"])
        with patch("builtins.input", side_effect=inputs):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                from mentor.cli import main

                ret = main(["--no-stream"])
        self.assertEqual(ret, 0)

    def test_single_ask_no_stream(self):
        inputs = iter(["这个功能因为底层 API 不稳定，所以还没上线", "quit"])
        with patch("builtins.input", side_effect=inputs):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                from mentor.cli import main

                ret = main(["--no-stream"])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
