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

## Deploy

### Frontend on GitHub Pages
This repo includes a Pages workflow (`.github/workflows/pages.yml`). To publish:
1. Push to `main`.
2. In your GitHub repo settings → Pages, set Source to "GitHub Actions". The `pages.yml` workflow will build and publish the static site.
3. Edit `assets/js/config.js` and set `window.ROOTSOURCE_API_BASE` to your backend URL, for example:
	`window.ROOTSOURCE_API_BASE = 'https://your-backend.example.com';`

### Backend hosting
Deploy the FastAPI backend to any host (Render, Railway, Fly.io, Cloud Run, EC2, VPS, etc.). Use the production command:
`gunicorn -c gunicorn.conf.py backend:app`

Environment variables to set:
- `GROQ_API_KEY` (optional; enables live LLM responses)
- `ALLOW_ORIGINS` to include your Pages origin, e.g. `https://<user>.github.io`
- `PORT` (many platforms set this automatically; our `gunicorn.conf.py` reads it)

Once deployed, ensure the backend URL is configured in `assets/js/config.js` as above.

## Notes
- If `GROQ_API_KEY` is not set, the backend returns a clear demo response and the app remains functional for UI testing.
- When hosting frontend separately (e.g., GitHub Pages), make sure `ALLOW_ORIGINS` includes the Pages domain.
