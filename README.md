# AI Workflow Copilot

> Turn documents and Gmail messages into summaries, action items, insights, or
> side-by-side comparisons — using a **local** LLM, then push the resulting tasks
> straight to Google Calendar.

A local-first PyQt5 desktop app powered by a local [Ollama](https://ollama.com)
model. Your documents and emails never leave your machine — the LLM runs locally.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-41CD52?logo=qt&logoColor=white)
![Ollama](https://img.shields.io/badge/LLM-Ollama%20(local)-000000)
![License](https://img.shields.io/badge/License-MIT-blue)

<!-- DEMO: record a ~30s clip of one full workflow, convert to GIF, save as docs/demo.gif -->
![Demo](docs/demo.gif)

---

## What this project demonstrates

A complete local-first AI pipeline built end to end:

- **Local LLM orchestration** — chunk long inputs, prompt a local Ollama model per
  workflow, parse the JSON it returns, and merge results across chunks.
- **Responsive desktop UI** — PyQt5 with workflows running on a background `QThread`
  so the interface never freezes (runs are cancellable mid-flight).
- **Real OAuth integration** — multi-account Google sign-in (Gmail read + Calendar
  write) with per-account token storage and refresh.
- **Privacy by design** — documents and email bodies are processed by a model
  running on the user's own machine; nothing is sent to a third-party API.

> **Note — this is a local-first desktop app, so there is no hosted "try it" demo.**
> It needs Ollama and a model running locally plus your own Google credentials. The
> GIF above and the screenshots below show it in action.

---

## Screenshots

<!-- Capture these while the app is running and save them under docs/screenshots/ -->

| Main window | Task review |
|---|---|
| ![Main window](docs/screenshots/main.png) | ![Task review dialog](docs/screenshots/task-review.png) |

| Run history | Settings |
|---|---|
| ![Run history](docs/screenshots/history.png) | ![Settings dialog](docs/screenshots/settings.png) |

---

## Features

- **Four workflows** — Summary, Tasks, Insights, Compare
- **Multi-source input** — paste text, drag-and-drop `.txt` / `.pdf`, batch
  upload, or fetch Gmail messages with native search syntax
  (`from:`, `subject:`, `is:unread`, …)
- **Multi-account Google sign-in** — add, switch, and remove Google accounts
  from the header dropdown; tokens are stored per account under `tokens/`
- **Task review dialog** — edit task title, deadline, and priority, or uncheck
  rows to skip, before any Calendar events are created
- **Tasks classifier** — returns a `source_type` label so narrative, reddit
  threads, and reference material don't get turned into fake action items
- **Cancellable runs** — the Process button doubles as Cancel during a run
- **Run history** — every result is stored in a local SQLite database and is
  searchable / reloadable in-app
- **TXT / CSV export**

---

## Architecture

```mermaid
flowchart TD
    subgraph Inputs
        F[File · .txt / .pdf]
        G[Gmail messages]
        T[Pasted text]
    end
    F & G & T --> IP["input_processing/<br/>handlers · cleaner · chunker · google_auth"]
    IP --> WE["core/workflow_engine.py<br/><i>orchestrator</i>"]
    WE --> PM["core/prompt_manager.py<br/>per-workflow prompt templates"]
    PM --> LR["core/llm_router.py"]
    LR --> OS["services/ollama_service.py<br/>local Ollama model"]
    OS --> OP["core/output_parser.py<br/>extracts JSON"]
    OP --> MR["merge_results()<br/>aggregates across chunks"]
    MR --> UI["ui/main_window.py<br/>display · review · export · history"]
    UI -->|approved tasks| CAL["services/calendar_service.py<br/>Google Calendar events"]
    UI --> DB[("storage/<br/>SQLite history")]
```

---

## Tech stack

**Python** · **PyQt5** (desktop UI) · **Ollama** + Mistral (local LLM) ·
**Google Gmail & Calendar APIs** (OAuth2) · **PyMuPDF** (PDF parsing) ·
**SQLite** (run history) · **pytest** + **ruff**

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd ai_workflow_copilot
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS / Linux
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
GMAIL_CLIENT_SECRET=client_secret.json
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral
CHUNK_SIZE=300
```

### 3. Start Ollama

```bash
ollama serve
ollama pull mistral
```

### 4. Run

```bash
python main.py
```

---

## Google setup

1. Open the [Google Cloud Console](https://console.cloud.google.com/) and
   create (or reuse) a project.
2. Enable **Gmail API** and **Google Calendar API** for that project.
3. Create OAuth 2.0 credentials (Application type: **Desktop app**) and
   download the JSON.
4. Save the JSON somewhere in the project folder and point
   `GMAIL_CLIENT_SECRET` in `.env` at it.
5. Launch the app and use the **Account** dropdown in the header → *"Add
   account…"* to complete the OAuth flow in the browser. Tokens are saved
   under `tokens/<email>.pkl`.

Required scopes:

- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/calendar.events`
- `https://www.googleapis.com/auth/userinfo.email`
- `openid`

---

## Output schemas

**Summary**
```json
{ "summary": "..." }
```

**Tasks**
```json
{
  "source_type": "actionable | narrative | discussion | informational",
  "action_items": [
    { "task": "...", "deadline": "...", "priority": "high|medium|low" }
  ]
}
```

**Insights**
```json
{ "key_insights": ["..."] }
```

**Compare**
```json
{
  "summary": "...",
  "common_themes": ["..."],
  "differences": ["..."],
  "key_insights": ["..."]
}
```

---

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Run the selected workflow (or cancel if running) |
| `Ctrl+O` | Open files |
| `Ctrl+E` | Fetch emails |
| `Ctrl+S` | Export result as TXT |
| `Ctrl+Shift+S` | Export result as CSV |
| `Ctrl+,` | Open Settings |
| `Ctrl+L` | Clear input |

---

## Testing

```bash
python -m pytest tests/ -v
```

Sample PDFs for manual testing of each workflow can be generated with:

```bash
python tests/generate_test_pdfs.py
```

They land in `tests/test_pdfs/` (gitignored).

---

## Project layout

```
ai_workflow_copilot/
├── config/             settings + persisted preferences
├── core/               workflow engine, LLM router, prompts, output parser
├── exports/            TXT / CSV exporters
├── input_processing/   file handlers, Gmail, OAuth, cleaner, chunker
├── services/           Ollama and Google Calendar clients
├── storage/            SQLite history
├── tests/              unit tests + PDF fixture generator
├── ui/                 PyQt5 main window, settings, task review dialog
├── utils/              logger and small helpers
├── main.py             entry point
├── requirements.txt
└── .env.example
```

---

## License

MIT — see [`LICENSE`](LICENSE).
