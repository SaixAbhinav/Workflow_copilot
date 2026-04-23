# AI Workflow Copilot

A local-first PyQt5 desktop app that turns documents and Gmail messages into
summaries, action items, insights, or side-by-side comparisons — powered by a
local Ollama model, with Google Calendar integration for pushing extracted
tasks.

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

```
Input (File / Gmail / Text)
        │
        ▼
 input_processing/  →  handlers · cleaner · chunker · google_auth
        │
        ▼
 core/workflow_engine.py    orchestrator
        │
        ▼
 core/prompt_manager.py     per-workflow prompt templates
        │
        ▼
 core/llm_router.py  →  services/ollama_service.py
        │
        ▼
 core/output_parser.py      extracts JSON
        │
        ▼
 merge_results()            aggregates across chunks
        │
        ▼
 ui/main_window.py          display · review · export · history
```

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

MIT — see `LICENSE` if included, otherwise feel free to use and adapt.
