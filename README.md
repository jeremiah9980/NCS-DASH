# NCS Dashboard

A web portal for monitoring National Championship Sports (NCS) fastpitch rosters across Central Texas — built for coaches and administrators of Texas Venom and similar programs.

## Features

- **Team browser** — view all monitored 10U / 12U Central Texas teams with division and city filters
- **Roster view** — current active roster for any team
- **Change history** — full log of every player added or removed
- **Search** — find teams or players by name, division, and city
- **AI agent** — structured query endpoint that translates natural-language-style inputs into DB queries
- **Slack notifications** — automatic webhook message on every roster change
- **Scheduled scraper** — runs every 4 hours via GitHub Actions

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Scraper | BeautifulSoup4, requests |
| Notifications | Slack Webhook (slack-sdk) |
| Frontend | React 18, Vite, React Router |
| CI/CD | GitHub Actions |

## Quick Start

### Backend

```bash
cp .env.example .env          # fill in SLACK_WEBHOOK_URL, etc.
pip install -r requirements.txt
uvicorn app.main:app --reload  # API at http://localhost:8000
```

API docs auto-generated at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev                    # UI at http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

### Scraper

```bash
# Set NCS_SEED_EVENT_IDS in .env (comma-separated NCS event IDs)
python -m scraper.ncs_scraper
```

The scraper also runs automatically every 4 hours via `.github/workflows/scraper.yml`.

## Configuration

All configuration is via environment variables (or a `.env` file):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./ncs_dash.db` | SQLAlchemy connection string |
| `SLACK_WEBHOOK_URL` | — | Incoming webhook URL |
| `NCS_SEED_EVENT_IDS` | — | Comma-separated NCS event IDs to monitor |
| `MONITORED_DIVISIONS` | `10U,12U` | Divisions to track |
| `MONITORED_CITIES` | `Austin,Cedar Park,...` | Cities to include |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed origins for the API |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/teams` | List teams (filter by `division`, `city`) |
| POST | `/teams` | Register a new team |
| GET | `/teams/{id}` | Get a team |
| GET | `/teams/{id}/roster` | Current active roster |
| GET | `/teams/{id}/history` | Roster change log |
| GET | `/search/teams` | Search teams by name/division/city |
| GET | `/search/players` | Search players by name |
| POST | `/agent/query` | Structured JSON query (see below) |
| GET | `/health` | Health check |

### Agent Query Format

```json
{
  "team": "CenTex Force",
  "player": null,
  "division": "10U",
  "city": "Austin",
  "date_from": "2024-01-01",
  "date_to": null
}
```

## Database Schema

```
teams           (id, ncs_id, name, division, city, region, roster_url)
players         (id, team_id, name, number, status)
snapshots       (id, team_id, captured_at)
snapshot_players(snapshot_id, player_id)
changes         (id, team_id, player_id, change_type, change_time)
```

## Running Tests

```bash
pytest tests/ -v
```

## Deployment

### Frontend — GitHub Pages

The frontend auto-deploys to GitHub Pages on every push to `main` that touches `frontend/**`, via `.github/workflows/deploy-pages.yml`. The live site is:

> **https://jeremiah9980.github.io/NCS-DASH/**

One-time setup:

1. In repo **Settings → Pages**, set **Source** to **GitHub Actions**.
2. In repo **Settings → Secrets and variables → Actions → Variables**, add a repository variable named `VITE_API_URL` pointing at your deployed backend (e.g. `https://ncs-dash-api.onrender.com`). Without this, the deployed site has no backend to call.
3. Push to `main` (or run the workflow manually via **Actions → Deploy Frontend to GitHub Pages → Run workflow**).

Because GitHub Pages only serves static files, routing uses `HashRouter` (URLs look like `.../#/teams/3`) so deep links and refreshes work without server-side rewrites.

### Backend — Serverless (recommended)

Deploy the FastAPI app to **AWS Lambda** via [Mangum](https://mangum.io/) or to **Railway / Render** as a Docker container. Set `DATABASE_URL` to a PostgreSQL connection string for production, and configure `CORS_ORIGINS` to include `https://jeremiah9980.github.io`.

### Backend — Docker (self-hosted)

```bash
docker build -t ncs-dash .
docker run -e DATABASE_URL=... -e SLACK_WEBHOOK_URL=... -p 8000:8000 ncs-dash
```

## Project Structure

```
ncs-dash/
├── app/
│   ├── main.py          FastAPI application
│   ├── config.py        Settings from env
│   ├── database.py      SQLAlchemy engine & session
│   ├── models/          ORM models (team, player, snapshot, change)
│   ├── schemas/         Pydantic schemas
│   └── routers/         Route handlers (teams, search, agent)
├── scraper/
│   ├── ncs_scraper.py   Roster scraper & change detector
│   └── slack_notifier.py Slack webhook helper
├── frontend/
│   └── src/
│       ├── pages/       Home, TeamDetail, Search, AgentChat
│       ├── components/  Navbar
│       ├── api.js       Axios wrappers
│       └── styles/      Texas Venom CSS theme
├── tests/               pytest suite
└── .github/workflows/   CI + scheduled scraper
```

## Roadmap

- [ ] Natural-language query support via Claude API
- [ ] CSV / JSON export for rosters and change logs
- [ ] Additional regions beyond Central Texas
- [ ] Admin authentication for managing monitored events
- [ ] Dark / light mode toggle
