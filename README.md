# Sports Betting Value Finder


A Flask web application that aggregates odds from multiple sportsbooks to identify profitable betting opportunities. Features include arbitrage detection, value bet identification, steam move alerts, and line movement tracking.

## Live Demo

This project is deployed on [Render](https://render.com)'s free tier as a portfolio demo. Read this before you judge the numbers you see:

**What it is:**
- The real Flask app, the real UI, and the real detection logic (`app/services/analyzer.py`, `odds_insights.py`) running against seeded fixture data (`seed_demo.py`).
- The fixture data is built to exercise every feature — an arbitrage opportunity, a couple of value bets, and a steam move alert are all seeded on purpose so you can see what the dashboard looks like when there's something to find.

**What it isn't:**
- **Not live odds.** The demo has no `ODDS_API_KEY` and runs with `ENABLE_SCHEDULER=false`, so it never calls The Odds API. Every game, price, and timestamp you see is synthetic.
- **Not persistent.** Render's free tier uses an ephemeral filesystem — the SQLite database is wiped on every redeploy, restart, and spin-down after inactivity. The app reseeds itself from `seed_demo.py` on every cold start (see `render.yaml`), so the data resets to the same fixture snapshot each time; nothing you do in the UI is saved long-term.
- **Not fast to wake up.** Free-tier services spin down after inactivity and take ~30–60s to cold-start on the next request.

If you want to see the app work against real odds, run it locally with your own [The Odds API](https://the-odds-api.com) key — see "Option 2: Local Development" below.

## Features

- **Odds Aggregation** - Pulls real-time odds from 15+ US sportsbooks via The Odds API
- **Arbitrage Detection** - Finds guaranteed profit opportunities across books
- **Value Bet Identification** - Flags odds that deviate from market consensus
- **Steam Move Alerts** - Detects coordinated line movements across multiple books
- **Line Movement Charts** - Visualizes how odds change over time
- **Smart Scheduling** - Increases fetch frequency as game time approaches

## Tech Stack

- **Backend**: Flask, SQLAlchemy, APScheduler
- **Frontend**: Jinja2, Tailwind CSS, Chart.js
- **Database**: SQLite (default) or PostgreSQL
- **Testing**: pytest with coverage reporting
- **CI/CD**: GitHub Actions (linting, type checking, tests, Docker build)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/SaitamaStack/betting-project.git
cd betting-project

# Copy environment template and add your API key
cp .env.example .env
# Edit .env and set ODDS_API_KEY and SECRET_KEY

# Run with Docker Compose
docker-compose up
```

Open http://localhost:5000

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env and set ODDS_API_KEY and SECRET_KEY

# Run the application
python run.py
```

Open http://127.0.0.1:5000

### Testing the UI with Demo Data (no API key needed)

To see what the dashboard looks like without a live `ODDS_API_KEY` (or without waiting on the scheduler), seed it with the same fixture data used by the Render demo:

```bash
# In your .env, set DEMO_MODE=true (it's false by default so this never
# runs by accident during normal local development)
echo "DEMO_MODE=true" >> .env

# Seed the demo fixtures (arbitrage, value bets, and a steam move alert)
python seed_demo.py

# Start the app as usual
python run.py
```

`seed_demo.py` is a no-op unless `DEMO_MODE=true` is set, and it refuses to run if `ENABLE_SCHEDULER=true` (to avoid mixing seeded rows with live-fetched ones). It's re-runnable — each run replaces only its own demo slice, identified by an internal `__private_demo_seed__` prefix, without touching any real data.

## Deploying the Demo to Render

`render.yaml` defines a free-tier Render Blueprint that builds the existing `Dockerfile` and overrides its start command to reseed demo data before every boot:

```bash
python seed_demo.py && gunicorn --bind 0.0.0.0:${PORT:-5000} run:app
```

Gunicorn binds to `$PORT` rather than a hardcoded port because Render assigns the port at runtime via that env var (it does not default to 5000) — a hardcoded bind would fail Render's port scan. `PORT` isn't set in `render.yaml`; Render provides it automatically.

To deploy your own copy: push this repo to your GitHub account, then in the Render dashboard choose **New > Blueprint** and point it at your fork. Render reads `render.yaml` and provisions the service with `DEMO_MODE=true`, `ENABLE_SCHEDULER=false`, and a generated `SECRET_KEY` — no `ODDS_API_KEY` is set, since this deployment is never meant to fetch live odds. See the "Live Demo" section above for what that means in practice.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ODDS_API_KEY` | Yes | - | API key from [The Odds API](https://the-odds-api.com) (free tier: 500 req/month) |
| `SECRET_KEY` | Yes | - | Flask secret key for sessions. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENABLE_SCHEDULER` | No | `false` | Enable background odds fetching |
| `DEMO_MODE` | No | `false` | Gates `seed_demo.py` and force-disables the scheduler; see "Live Demo" above |
| `ARB_THRESHOLD_PERCENT` | No | `1.0` | Minimum arbitrage profit % to flag |
| `VALUE_THRESHOLD_PERCENT` | No | `3.0` | Minimum edge % to flag as value |

See `.env.example` for all available options.

## Dashboard Guide

- **Best Lines** - Shows the best available price for each side of every market
- **Steam Moves** - Amber badge appears when 3+ books move in the same direction within 15 minutes
- **Line Movement Chart** - Click into a game to see historical odds changes

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_analyzer.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy app
```

### Project Structure

```
betting-project/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py             # SQLAlchemy models
│   ├── routes/               # Flask blueprints
│   │   ├── api.py            # JSON API endpoints
│   │   ├── dashboard.py      # Main dashboard
│   │   └── games.py          # Game detail pages
│   ├── services/             # Business logic
│   │   ├── analyzer.py       # Arbitrage & value detection
│   │   ├── normalizer.py     # Odds format conversion
│   │   ├── odds_fetcher.py   # API client
│   │   └── odds_insights.py  # Best lines & steam detection
│   ├── jobs/
│   │   └── scheduler.py      # Background job scheduling
│   └── templates/            # Jinja2 HTML templates
├── tests/                    # pytest test suite
├── seed_demo.py             # Demo fixture data (gated by DEMO_MODE)
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Local development orchestration
├── render.yaml              # Render Blueprint for the free-tier demo deploy
└── pyproject.toml          # Python tooling configuration
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/games` | GET | List upcoming games with latest odds |
| `/api/games/<id>/history` | GET | Historical odds snapshots for a game |
| `/api/opportunities` | GET | Current arbitrage and value bet alerts |
| `/api/status` | GET | Scheduler status and last fetch info |

## License

MIT
