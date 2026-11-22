# AI News Aggregator

An advanced, portfolio-ready news intelligence platform built with **FastAPI, React, SQLite/PostgreSQL-ready SQLAlchemy, RSS feeds, and an optional LLM summarization provider**.

It collects articles from configurable RSS feeds, normalizes and deduplicates them, ranks stories by relevance, generates concise summaries, and exposes search, topic, source, and analytics endpoints. The default experience works without paid API keys by using deterministic extractive summaries.

> Important: This is a working portfolio application, not a claim of affiliation with any news publisher. Respect each feed's terms, rate limits, and copyright. Store metadata and short summaries; link users to original publishers for full articles.

## Features

- Multi-source RSS ingestion with per-feed error isolation.
- Canonical URL and content-fingerprint deduplication.
- Article metadata extraction, topic tagging, and keyword search.
- Relevance ranking using recency, source diversity, and keyword matches.
- Extractive summaries out of the box; optional OpenAI-compatible LLM summarization.
- Saved articles and read/unread state.
- Background ingestion trigger and ingestion-run history.
- Dashboard analytics: source counts, topic distribution, daily volume.
- FastAPI REST API with Swagger docs.
- React + Vite dashboard with search, topic filters, saved list, and article cards.
- Docker Compose, CI workflow, tests, and configurable feeds.

## Architecture

```text
RSS / Atom Feeds
      |
      v
Feed Fetcher (timeouts, retries, isolated failures)
      |
      v
Normalizer + Deduplicator
      |
      v
Topic Tagger + Relevance Ranker
      |
      v
Summarizer (extractive default / optional LLM)
      |
      v
SQLAlchemy Database
      |
      +---- FastAPI REST API ---- React Dashboard
```

## Quick start with Docker

Requirements: Docker Desktop.

```bash
cp .env.example .env
docker compose up --build
```

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

Trigger ingestion:

```bash
curl -X POST http://localhost:8000/api/ingest
```

Browse articles:

```bash
curl "http://localhost:8000/api/articles?limit=20"
curl "http://localhost:8000/api/articles?topic=technology"
curl "http://localhost:8000/api/analytics"
```

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (second terminal):

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env` if needed.

## Optional LLM summaries

The project runs without an LLM key. To enable an OpenAI-compatible chat-completions endpoint, set:

```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_key
LLM_MODEL=your_available_model
```

The summarizer sends only the article title and feed-provided description/content. If the provider is unavailable, it safely falls back to extractive summarization. Never commit real API keys.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/ingest` | Trigger background RSS ingestion |
| GET | `/api/articles` | Search/filter/sort articles |
| GET | `/api/articles/{id}` | Article details |
| POST | `/api/articles/{id}/save` | Save article |
| DELETE | `/api/articles/{id}/save` | Unsave article |
| GET | `/api/saved` | List saved articles |
| GET | `/api/analytics` | Dashboard metrics |
| GET | `/api/runs` | Ingestion history |

## Configuration

Copy `.env.example` to `.env`. Edit `backend/app/feeds.py` to add or remove RSS feeds. Feeds are examples and availability can change; a failed feed does not stop the other sources.

## Tests

```bash
cd backend
pytest -q
```

Tests use mocked feed responses and an isolated SQLite database; they do not require external network access or API keys.

## Security and responsible use

- Keep provider API keys in environment variables.
- Do not scrape publisher pages to bypass paywalls or access controls.
- Use RSS metadata and short descriptions in line with publisher terms.
- Link to original articles and preserve attribution.
- This demo does not provide financial, medical, or other professional advice.

## Suggested resume bullets (only after running and verifying)

- Built a multi-source news intelligence platform using FastAPI and React, with RSS ingestion, canonical URL deduplication, topic tagging, relevance ranking, and searchable article discovery.
- Implemented optional LLM-powered summaries with deterministic fallback, saved-article workflows, ingestion observability, analytics, Docker Compose, and automated CI tests.
