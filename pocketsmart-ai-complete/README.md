# PocketSmart AI

A complete FastAPI implementation of the PocketSmart AI project: budget-aware recommendations for Home Interiors, Party Planning, and Jewelry.

## Features
- FastAPI backend + Jinja2 responsive frontend
- Register/login/logout with hashed passwords and JWT stored in an HttpOnly cookie
- JSON APIs for Home and Party planners
- Multipart API for Jewelry planner with optional image input
- Google GenAI SDK integration with configurable Gemini model
- Graceful deterministic fallback recommendations when no Gemini key is configured or an AI request fails
- SQLite history storage and recommendation detail pages
- Marketplace search links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO (no unsupported claim of live inventory/pricing)
- CORS, upload validation, Pydantic validation, tests, VS Code launch config

## 1. Prerequisites
- Python 3.11 or newer
- VS Code with the Python extension
- Optional: Gemini API key from Google AI Studio / Gemini API

## 2. Open in VS Code
Open the `pocketsmart-ai` folder in VS Code, then open **Terminal → New Terminal**.

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 3. Configure `.env`
At minimum, change `SECRET_KEY`.

To enable Gemini:
```env
GEMINI_API_KEY=your_real_api_key
USE_GEMINI=true
GEMINI_MODEL=gemini-3.8-flash
```

If you leave `GEMINI_API_KEY` empty, the full app still works using the built-in fallback engine.

## 4. Run
```bash
uvicorn app.main:app --reload
```
Live demo: https://pocketsmart-ai-mkxq.onrender.com

Open: http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health

You can also press **F5** in VS Code and select `PocketSmart AI (FastAPI)`.

## 5. Test
```bash
pytest -q
```
Tests deliberately disable Gemini so they are repeatable and do not spend API quota.

## Core routes
- `/`, `/register`, `/login`, `/logout`, `/dashboard`
- `/planner/home`, `/planner/party`, `/planner/jewelry`
- `/history`, `/recommendation/{id}`, `/testimonials`
- `POST /api/generate-home`
- `POST /api/generate-party`
- `POST /api/generate-jewelry`
- `GET /api/recommendations-details/{id}`
- `POST /token`, `GET /session-info`, `GET /session-data`
- `GET /startup`, `GET /health`

## Important implementation note
The source documentation alternates between Flask and FastAPI. This build follows the later and more detailed FastAPI milestones, route definitions, Jinja2 frontend, CORS, JWT/session, and `main.py` architecture. The documentation also mentions third-party marketplace APIs but supplies no API contracts or credentials, so this implementation generates marketplace search links instead of scraping or fabricating live product data.
