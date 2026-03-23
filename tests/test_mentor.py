"""Tests for the R&D Career English Mentor."""

from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers – build a minimal mock of the openai package so that tests work
# even when the real package is not installed.
# ---------------------------------------------------------------------------

def _make_openai_mock() -> types.ModuleType:
    """Return a lightweight mock of the openai package."""
    mock_openai = MagicMock()

    # Simulate a successful chat completion response
    choice = MagicMock()
    choice.message.content = (
        "### 【地道表达】(The Natural Way)\n"
        "The rollout of this feature is on hold due to the instability "
        "of the underlying API.\n\n"
        "### 【关键术语】(Key Tech Terms)\n"
        "- **Rollout**: 上线/发布\n"
        "- **Underlying**: 底层\n\n"
        "### 【避坑指南】(Common Pitfalls)\n"
        "Avoid 'not online'; prefer 'pushed to production' or 'deployed'.\n\n"
        "### 【实战练习】(Practice)\n"
        "Try: 'The new payment service hasn't been deployed yet because of "
        "dependency issues.'"
    )

    completion = MagicMock()
    completion.choices = [choice]

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = completion

    mock_openai.OpenAI.return_value = mock_client_instance
    return mock_openai


# ---------------------------------------------------------------------------
# Patch openai before importing the module under test
# ---------------------------------------------------------------------------

_openai_mock = _make_openai_mock()
sys.modules.setdefault("openai", _openai_mock)

# Now safe to import
from mentor.mentor import RDEnglishMentor  # noqa: E402
from mentor.prompt import SYSTEM_PROMPT  # noqa: E402


class TestSystemPrompt(unittest.TestCase):
    """Validate that the system prompt contains the required sections."""

    def test_prompt_contains_role_description(self):
        self.assertIn("Silicon Valley", SYSTEM_PROMPT)

    def test_prompt_contains_all_output_sections(self):
        for section in [
            "【地道表达】",
            "【关键术语】",
            "【避坑指南】",
            "【实战练习】",
        ]:
            with self.subTest(section=section):
                self.assertIn(section, SYSTEM_PROMPT)

    def test_prompt_contains_key_scenarios(self):
        for keyword in ["Stand-up", "Design Review", "Code Review"]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, SYSTEM_PROMPT)


class TestRDEnglishMentorInit(unittest.TestCase):
    """Test initialisation of RDEnglishMentor."""

    def test_raises_when_no_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            # Make sure OPENAI_API_KEY is not set
            import os
            os.environ.pop("OPENAI_API_KEY", None)
            with self.assertRaises(ValueError):
                RDEnglishMentor(api_key=None)

    def test_initialises_with_explicit_api_key(self):
        mentor = RDEnglishMentor(api_key="sk-test-key")
        self.assertIsNotNone(mentor)

    def test_initialises_with_env_api_key(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-env-key"}):
            mentor = RDEnglishMentor()
            self.assertIsNotNone(mentor)

    def test_default_model(self):
        mentor = RDEnglishMentor(api_key="sk-test-key")
        self.assertEqual(mentor._model, RDEnglishMentor.DEFAULT_MODEL)

    def test_custom_model(self):
        mentor = RDEnglishMentor(api_key="sk-test-key", model="gpt-4-turbo")
        self.assertEqual(mentor._model, "gpt-4-turbo")


class TestRDEnglishMentorCoach(unittest.TestCase):
    """Test the coach() method."""

    def setUp(self):
        self.mentor = RDEnglishMentor(api_key="sk-test-key")

    def test_coach_returns_string(self):
        result = self.mentor.coach(
            "这个功能因为底层 API 不稳定，所以还没上线"
        )
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_coach_response_contains_expected_sections(self):
        result = self.mentor.coach(
            "这个功能因为底层 API 不稳定，所以还没上线"
        )
        for section in ["【地道表达】", "【关键术语】", "【避坑指南】", "【实战练习】"]:
            with self.subTest(section=section):
                self.assertIn(section, result)

    def test_coach_appends_to_history(self):
        self.mentor.coach("我想说这个 PR 需要更多测试")
        # history should contain user + assistant messages
        self.assertEqual(len(self.mentor._history), 2)
        self.assertEqual(self.mentor._history[0]["role"], "user")
        self.assertEqual(self.mentor._history[1]["role"], "assistant")

    def test_multiple_turns_accumulate_history(self):
        self.mentor.coach("第一条消息")
        self.mentor.coach("第二条消息")
        self.assertEqual(len(self.mentor._history), 4)

    def test_reset_clears_history(self):
        self.mentor.coach("随便说点什么")
        self.mentor.reset()
        self.assertEqual(len(self.mentor._history), 0)


class TestRDEnglishMentorBuildMessages(unittest.TestCase):
    """Test the internal _build_messages helper."""

    def setUp(self):
        self.mentor = RDEnglishMentor(api_key="sk-test-key")

    def test_first_message_is_system(self):
        self.mentor._history = [{"role": "user", "content": "test"}]
        messages = self.mentor._build_messages()
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], SYSTEM_PROMPT)

    def test_user_message_follows_system(self):
        user_msg = "test message"
        self.mentor._history = [{"role": "user", "content": user_msg}]
        messages = self.mentor._build_messages()
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], user_msg)


class TestCLI(unittest.TestCase):
    """Smoke tests for the CLI module."""

    def test_cli_single_shot_success(self):
        from mentor.cli import main

        with patch("mentor.cli.RDEnglishMentor") as MockMentor:
            instance = MockMentor.return_value
            instance.coach.return_value = "Mocked response with all four sections."
            rc = main(["--api-key", "sk-test", "这个 Bug 的优先级很高"])
        self.assertEqual(rc, 0)
        instance.coach.assert_called_once_with("这个 Bug 的优先级很高")

    def test_cli_exits_on_missing_api_key(self):
        from mentor.cli import main

        with patch("mentor.cli.RDEnglishMentor", side_effect=ValueError("no key")):
            rc = main(["some input"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
