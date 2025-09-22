# RootSource AI

A FastAPI-based AI assistant for farming and agriculture with a simple SPA frontend.

## Features
- FastAPI backend with health check and SPA static serving
- LLM integration via Groq (LangChain `ChatOpenAI`)
- DuckDuckGo Search tool for current info
- Robust formatting and multilingual support (detect + translate)
- CORS enabled for local development

## Requirements
- Python 3.11+ recommended
- A Groq API key (optional for demo mode)

## Setup
1. Create and activate a virtualenv
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment
```bash
cp .env.example .env
# edit .env and set GROQ_API_KEY
# optionally set ALLOW_ORIGINS (comma-separated), HOST, PORT
```

## Run (dev)
- With Uvicorn hot reload:
```bash
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

- Or via Makefile:
```bash
make dev
```

Then open `index.html` directly or visit `http://127.0.0.1:8000/`.

## Production run
Using Gunicorn + Uvicorn worker:
```bash
make start
# or
gunicorn -c gunicorn.conf.py backend:app
```

## Docker
```bash
docker build -t rootsource:latest .
docker run --rm -p 8000:8000 --env-file .env rootsource:latest
```

## Tests
```bash
pytest -q
```

## VS Code tasks
Press `Ctrl+Shift+B` to see run tasks, or open `.vscode/tasks.json`.

## Notes
- If `GROQ_API_KEY` is not set, the backend returns a clear demo response and the app remains functional for UI testing.
- Frontend uses `fetch` to `http://127.0.0.1:8000/chat`. Adjust if deploying behind a different host.
