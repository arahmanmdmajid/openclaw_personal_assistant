# Hermes Personal Assistant

A personal AI assistant for **developer productivity**, built on the **Hermes Agent** framework (Option B). Receives messages via **Telegram**, routes them to specialized agents, and responds with actionable results.

---

## Architecture Overview

```
User (Telegram)
      │
      ▼
┌─────────────────────────────────────┐
│         Telegram Channel            │  ← Communication Layer
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│        Hermes Orchestrator          │  ← Routing & Logging
│  (keyword-based agent routing)      │
└───────┬──────────┬──────────┬───────┘
        │          │          │
        ▼          ▼          ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐
 │ Research │ │ Planning │ │  Code    │  ← Agents
 │  Agent   │ │  Agent   │ │  Agent   │
 └────┬─────┘ └────┬─────┘ └────┬─────┘
      │             │             │
      ▼             ▼             ▼
┌─────────────────────────────────────┐
│               Skills                │
│  WebSearch | Summarization | Tasks  │
│  TaskExtraction | CodeAnalysis      │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│             External Tools          │
│   DuckDuckGo Search | GitHub API   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           Model Manager             │
│   Claude (Anthropic) | Ollama       │
└─────────────────────────────────────┘
```

---

## A. Communication Channel — Telegram

- **Bot library**: `python-telegram-bot` v21
- Users send messages directly in Telegram
- Bot routes to the correct agent and replies in the same chat
- Supports user-ID allowlist for access control

**Bot Commands:**
| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Usage instructions |
| `/model claude` | Switch to Claude backend |
| `/model ollama` | Switch to Ollama (local) |
| `/log` | Show last 5 conversation entries |
| `/benchmark` | Compare Claude vs Ollama live |

---

## B. Use Case Workflow

**Scenario: Developer asks for a GitHub repo status + plan**

```
User (Telegram): "Check open issues at github.com/pallets/flask and 
                  create a plan to fix the top 3."

Step 1: Telegram Channel receives the message
Step 2: Orchestrator detects "github.com/" → routes to Code Agent
Step 3: Code Agent calls GitHubTool → fetches open issues & commits
Step 4: Code Agent calls CodeAnalysisSkill → synthesizes findings
Step 5: Response sent back to Telegram with agent/skill/model metadata
```

**Full workflow screenshot:** see `demo/screenshots/`

---

## C. Agents

| Agent | File | Responsibility | Triggered By |
|-------|------|----------------|--------------|
| **Research Agent** | `agents/research_agent.py` | Searches the web and synthesizes research briefs | "search", "find", "summarize", "what is", "latest news" |
| **Planning Agent** | `agents/planning_agent.py` | Breaks down goals into task lists, roadmaps, schedules | "plan", "task", "schedule", "roadmap", "priority" |
| **Code Agent** | `agents/code_agent.py` | Reviews/debugs/explains code; fetches GitHub data | "code", "bug", "review", "github.com/", `` ``` `` blocks |

---

## D. Skills

| Skill | File | What it does | Input | Output |
|-------|------|-------------|-------|--------|
| **Web Search** | `skills/web_search_skill.py` | Searches DuckDuckGo for real-time information | `query`, `max_results` | List of `{title, url, snippet}` |
| **Summarization** | `skills/summarization_skill.py` | Condenses long text into bullet-point key findings | `text`, `max_bullets` | Bulleted summary string |
| **Task Extraction** | `skills/task_extraction_skill.py` | Extracts actionable to-do items from any text | `text`, `max_tasks` | Numbered task list string |
| **Code Analysis** | `skills/code_analysis_skill.py` | Reviews, explains, or debugs code snippets | `code`, `language`, `mode` | Structured code review string |

---

## E. External Tools

| Tool | File | API Used | Auth Required |
|------|------|---------|---------------|
| **DuckDuckGo Search** | `tools/search_tool.py` | DuckDuckGo (via `duckduckgo-search`) | ❌ None |
| **GitHub API** | `tools/github_tool.py` | GitHub REST API (via `PyGithub`) | ✅ `GITHUB_TOKEN` (optional for public repos) |

---

## F. Model Comparison

| Model | Setup | Speed | Response Quality | Tool Use Accuracy | Cost | Notes |
|-------|-------|-------|-----------------|-------------------|------|-------|
| **Claude Sonnet 4.6** | API (Anthropic) | Fast (~2–4s) | Excellent | Excellent — follows instructions precisely | Paid (~$3/M input tokens) | Best for complex reasoning, code review, structured output |
| **Ollama Hermes-3 (local)** | Local (Ollama) | Medium (~5–15s, CPU) | Good | Good — occasionally misses format constraints | Free | No internet required; weaker on multi-step tool use |

**Key findings:**
- Claude excels at structured output, code analysis, and multi-step tasks
- Ollama Hermes-3 is a strong free alternative for simple Q&A and planning
- Claude is significantly faster when hardware GPU is unavailable
- Ollama has zero marginal cost, making it ideal for high-frequency testing

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/hermes-personal-assistant.git
cd hermes-personal-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your keys:
# - ANTHROPIC_API_KEY  (get at console.anthropic.com)
# - TELEGRAM_BOT_TOKEN (create bot via @BotFather on Telegram)
# - GITHUB_TOKEN       (optional; needed for private repos)
```

### 5a. Run the Telegram bot

```bash
python main.py
# or with Ollama backend:
python main.py --backend ollama
```

### 5b. Run the CLI demo (no Telegram token needed)

```bash
python main.py --demo
# or:
python demo/demo_cli.py
```

### 5c. Run model comparison

```bash
python demo/model_comparison.py
```

### 6. Install Ollama (for local model)

```bash
# Download from https://ollama.com
ollama pull hermes3
# or:
ollama pull mistral
```

### 7. Run tests

```bash
pip install pytest
pytest tests/
```

---

## Project Structure

```
hermes-personal-assistant/
├── main.py                        # Entry point
├── orchestrator.py                # Agent router + conversation log
├── config.py                      # Environment variable management
├── requirements.txt
├── .env.example
├── agents/
│   ├── base_agent.py              # Abstract base class
│   ├── research_agent.py          # Research & summarization
│   ├── planning_agent.py          # Task planning & roadmaps
│   └── code_agent.py              # Code review & GitHub integration
├── skills/
│   ├── base_skill.py              # Abstract base class
│   ├── web_search_skill.py        # DuckDuckGo search
│   ├── summarization_skill.py     # LLM-powered summarization
│   ├── task_extraction_skill.py   # Action item extraction
│   └── code_analysis_skill.py     # Code review/debug/explain
├── tools/
│   ├── search_tool.py             # DuckDuckGo wrapper
│   └── github_tool.py             # GitHub API wrapper
├── channels/
│   └── telegram_channel.py        # Telegram bot integration
├── models/
│   └── model_manager.py           # Claude + Ollama backend
├── demo/
│   ├── demo_cli.py                # CLI demo (no Telegram needed)
│   └── model_comparison.py        # Side-by-side model benchmark
└── tests/
    └── test_orchestrator.py       # Routing unit tests
```

---

## Security Notes

- All API keys are stored in `.env` (never committed — add to `.gitignore`)
- Telegram bot enforces user-ID allowlist via `TELEGRAM_ALLOWED_USER_IDS`
- GitHub token uses minimum required scopes (read-only for public repos)
- No file system write access is granted to agents
- Human-readable conversation logs stored in-memory only (not persisted)

---

## Reflection

**What worked well:**
- Keyword-based routing is fast and surprisingly accurate for single-domain queries
- Claude's structured output made it easy to extract bullet points and task lists
- DuckDuckGo search requires no API key and works reliably

**What failed / limitations:**
- Multi-domain messages (e.g., "search AND plan") get routed to only one agent — a multi-agent pipeline would be better
- Ollama performance is heavily hardware-dependent; CPU inference is slow
- Telegram's Markdown parser occasionally requires escaping special characters

**Which model performed best?**
- Claude Sonnet 4.6 was consistently superior for code review, structured planning, and tool-use accuracy
- Ollama Hermes-3 was acceptable for simple Q&A and needed no API costs

**How did the assistant improve workflow?**
- Reduced context-switching between browser, GitHub, and notes apps
- Code reviews that took 10+ minutes now take ~30 seconds

**What to improve next:**
- Add vector database (ChromaDB/Pinecone) for long-term document memory
- Add memory of past conversations per user
- Implement multi-agent pipelines for compound tasks
- Add human approval step before sending GitHub comments or emails
- Deploy on a VPS with webhook instead of polling
