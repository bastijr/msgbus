# msgbus

A high-performance C++ message bus framework built on ZeroMQ + Protobuf, supporting method/notify RPC, topic subscription, extensible serialization, config hot-reload, multiprocess, and full test/benchmark coverage. Suitable for high-throughput interprocess or embedded communication scenarios.

- Supports method/notify, multiple channels, and topic subscription
- Protobuf schema for structured, extensible messages
- CMake cross-platform build system
- Includes usage samples, unit tests, and performance tests

---

## 🤖 R&D Career English Mentor | 研发职场英语导师

A conversational AI tool that helps Chinese-speaking engineers communicate more naturally and professionally in English during:

- **Stand-up meetings** (站会)
- **Design Reviews** (设计评审)
- **Code Reviews** (代码评审)
- **Technical Discussions** (技术讨论)

### Features

| Feature | Description |
|---|---|
| **Terminology Correction** | Identifies and corrects Chinglish; provides industry-standard vocabulary |
| **Scenario Simulation** | Simulates real R&D scenarios (bug priority, system latency, Sprint sync) |
| **Expression Upgrade** | Offers expressions at different tones, especially diplomatic phrasing for reviews |
| **Culture Navigation** | Explains workplace communication "subtext" and North American/European R&D norms |

### Structured Output

Every response is structured into four sections:

- **【地道表达】 (The Natural Way)** — 1–2 natural sentence patterns used by R&D teams
- **【关键术语】 (Key Tech Terms)** — Explanations of professional vocabulary (e.g., Trade-off, Bottleneck, Scalability, Regression)
- **【避坑指南】 (Common Pitfalls)** — Common grammar mistakes, inappropriate word choices, and better alternatives
- **【实战练习】 (Practice)** — A similar R&D scenario to apply the newly learned expressions

### Installation

```bash
pip install -r requirements.txt
```

### Usage

**Interactive CLI** (requires an OpenAI API key):

```bash
export OPENAI_API_KEY="sk-..."
python -m mentor.cli
# or after installing as a package:
mentor
```

**Python API**:

```python
from mentor import MentorSession

session = MentorSession()  # reads OPENAI_API_KEY from environment
response = session.ask("这个功能因为底层 API 不稳定，所以还没上线")
print(response.format())
```

**Example output**:

```
**【地道表达】 (The Natural Way)**
- "The rollout of this feature is on hold due to the instability of the underlying API."
- "We're holding off on deploying this feature because the underlying API has been unreliable."

**【关键术语】 (Key Tech Terms)**
- **Rollout**: The gradual or phased deployment of a feature or update to production.
- **Underlying**: Refers to the foundational layer (e.g., underlying API, underlying infrastructure).
- **On hold**: Temporarily paused or delayed.

**【避坑指南】 (Common Pitfalls)**
- ❌ "This feature is not online yet." → Sounds unnatural; use "deployed" or "rolled out."
- ❌ "Because...so..." as a pair → Use one conjunction only.

**【实战练习】 (Practice)**
Try: "这个 PR 因为测试覆盖率不够，所以还没合并。"
Use terms like "merge," "test coverage," and "pending."
```

### CLI Options

| Option | Default | Description |
|---|---|---|
| `--model MODEL` | `gpt-4o` | OpenAI chat model to use |
| `--api-key KEY` | env `OPENAI_API_KEY` | OpenAI API key |
| `--no-stream` | streaming | Wait for the full response before printing |

### Running Tests

```bash
python -m pytest tests/test_mentor.py -v
```

### Project Structure

```
mentor/
├── __init__.py      # Public API
├── prompt.py        # System prompt defining the mentor's persona and output format
├── core.py          # Response parsing and formatting logic
├── session.py       # OpenAI-backed conversation session
└── cli.py           # Interactive command-line interface
tests/
└── test_mentor.py   # Unit tests (no live API calls required)
requirements.txt     # Python dependencies
```