# Sports Betting Value Finder

Aggregates odds from multiple sportsbooks, identifies arbitrage opportunities and value bets, tracks line movements over time.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```
ODDS_API_KEY=your_api_key_here
```

Get a free API key at https://the-odds-api.com (500 requests/month).

Optional variables:
- `FETCH_INTERVAL_MINUTES` - How often to fetch odds (default: 15)
- `ARB_THRESHOLD_PERCENT` - Minimum arbitrage profit to alert (default: 1.0)
- `VALUE_THRESHOLD_PERCENT` - Minimum edge to flag as value (default: 3.0)

## Run

```bash
python run.py
```

Open http://127.0.0.1:5000

## Tests

```bash
pytest
```
