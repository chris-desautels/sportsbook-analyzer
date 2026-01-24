# Sports Betting Value Finder

Aggregates odds from multiple sportsbooks, highlights best lines, flags steam moves, identifies arbitrage opportunities and value bets, and tracks line movements over time.

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
- `FETCH_INTERVAL_DEFAULT_MINUTES` - Default fetch interval in minutes (default: 60)
- `FETCH_INTERVAL_NEAR_HOURS` - Hours before kickoff to use the near interval (default: 3)
- `FETCH_INTERVAL_NEAR_MINUTES` - Fetch interval within the near window (default: 15)
- `FETCH_INTERVAL_IMMINENT_HOURS` - Hours before kickoff to use the imminent interval (default: 1)
- `FETCH_INTERVAL_IMMINENT_MINUTES` - Fetch interval within the imminent window (default: 5)
- `ARB_THRESHOLD_PERCENT` - Minimum arbitrage profit to alert (default: 1.0)
- `VALUE_THRESHOLD_PERCENT` - Minimum edge to flag as value (default: 3.0)
- `STEAM_WINDOW_MINUTES` - Steam detection window in minutes (default: 15)
- `STEAM_MIN_BOOKS` - Minimum books required for a steam signal (default: 3)
- `STEAM_MIN_PRICE_MOVE` - Minimum odds move (American) for steam (default: 20)
- `STEAM_MIN_POINT_MOVE` - Minimum point move for spreads/totals (default: 0.5)

## Dashboard Tips

- Best lines show the strongest price per side for each market.
- Steam move indicators appear when multiple books shift in the same direction within the configured window.
- Use Pin/Unpin to keep key games at the top of the dashboard list.

## Run

```bash
python run.py
```

Open http://127.0.0.1:5000

## Tests

```bash
pytest
```

## CI

GitHub Actions runs `pytest` on pushes and pull requests.
