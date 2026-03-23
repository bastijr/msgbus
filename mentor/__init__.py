"""R&D Career English Mentor package.

A conversational tool that helps Chinese-speaking engineers communicate
more naturally and professionally in:
- Stand-up meetings
- Design Reviews
- Code Reviews
- Technical Discussions

Usage
-----
From the command line::

    mentor

From Python::

    from mentor import MentorSession

    session = MentorSession()          # uses OPENAI_API_KEY env var
    response = session.ask("这个功能因为底层 API 不稳定，所以还没上线")
    print(response.format())
"""

from .core import MentorResponse, build_user_message, parse_response
from .prompt import SYSTEM_PROMPT
from .session import MentorSession

__all__ = [
    "MentorResponse",
    "MentorSession",
    "SYSTEM_PROMPT",
    "build_user_message",
    "parse_response",
]
