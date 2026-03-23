# msgbus

A high-performance C++ message bus framework built on ZeroMQ + Protobuf, supporting method/notify RPC, topic subscription, extensible serialization, config hot-reload, multiprocess, and full test/benchmark coverage. Suitable for high-throughput interprocess or embedded communication scenarios.

- Supports method/notify, multiple channels, and topic subscription
- Protobuf schema for structured, extensible messages
- CMake cross-platform build system
- Includes usage samples, unit tests, and performance tests

---

## 🤖 R&D Career English Mentor — 研发职场英语导师

An AI-powered coaching tool that helps Chinese engineers communicate more naturally and professionally during **Stand-ups**, **Design Reviews**, **Code Reviews**, and **Technical Discussions**.

### Features

| Section | Description |
|---|---|
| 【地道表达】(The Natural Way) | 1–2 industry-standard sentence patterns for the requested meaning |
| 【关键术语】(Key Tech Terms) | Key professional terms extracted and explained (Trade-off, Rollout, Scalability…) |
| 【避坑指南】(Common Pitfalls) | Grammar mistakes, word-choice errors, and Chinglish patterns to avoid |
| 【实战练习】(Practice) | A similar R&D scenario to practice with |

### Quick Start

**Install dependencies**

```bash
pip install -r requirements.txt
# or
pip install openai
```

**Set your OpenAI API key**

```bash
export OPENAI_API_KEY="sk-..."
```

**Interactive mode** (multi-turn conversation)

```bash
python -m mentor.cli
```

```
╔══════════════════════════════════════════════════════╗
║  🤖  R&D Career English Mentor  研发职场英语导师      ║
║  Type a sentence you want to express in English.     ║
║  Type 'quit' or 'exit' to leave. 'reset' to restart. ║
╚══════════════════════════════════════════════════════╝

You: 这个功能因为底层 API 不稳定，所以还没上线
```

**Single-shot mode**

```bash
python -m mentor.cli "这个功能因为底层 API 不稳定，所以还没上线"
```

**Example output**

```
### 【地道表达】(The Natural Way)
The rollout of this feature is on hold due to the instability of the underlying API.

### 【关键术语】(Key Tech Terms)
- **Rollout** (上线/发布): The process of gradually deploying a feature to production.
- **Underlying** (底层的): Describes the foundational layer a system depends on.
- **On hold** (暂停/搁置): Paused indefinitely, usually pending a blocker being resolved.

### 【避坑指南】(Common Pitfalls)
❌ "This feature is not online yet." — "online" doesn't carry the deployment meaning here.
✅ Use "deployed", "pushed to production", or "rolled out" instead.
Don't say "because the API is not stable". Prefer "due to API instability" or
"owing to intermittent API issues".

### 【实战练习】(Practice)
Try to express: "我们的数据迁移脚本因为第三方服务超时，一直没有跑完。"
```

### Python API

```python
from mentor import RDEnglishMentor

mentor = RDEnglishMentor(api_key="sk-...")

# Single response
response = mentor.coach("这个 PR 还有一些 edge case 没有覆盖到")
print(response)

# Streaming response (token by token)
for chunk in mentor.stream_coach("我们需要 refactor 这部分代码"):
    print(chunk, end="", flush=True)

# Reset conversation history
mentor.reset()
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Project Layout

```
mentor/
├── __init__.py   # Package exports
├── prompt.py     # System prompt definition
├── mentor.py     # RDEnglishMentor class
└── cli.py        # Command-line interface
tests/
└── test_mentor.py
requirements.txt
pyproject.toml
```