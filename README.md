# Sports Betting Value Finder

[![CI](https://github.com/SaitamaStack/betting-project/actions/workflows/ci.yml/badge.svg)](https://github.com/SaitamaStack/betting-project/actions/workflows/ci.yml)

A Flask web application that aggregates odds from multiple sportsbooks to identify profitable betting opportunities. Features include arbitrage detection, value bet identification, steam move alerts, and line movement tracking.

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

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ODDS_API_KEY` | Yes | - | API key from [The Odds API](https://the-odds-api.com) (free tier: 500 req/month) |
| `SECRET_KEY` | Yes | - | Flask secret key for sessions. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENABLE_SCHEDULER` | No | `false` | Enable background odds fetching |
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
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Local development orchestration
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
