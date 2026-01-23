from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OddsSnapshotPayload:
    sport_key: str
    sport_title: str
    external_game_id: str
    home_team: str
    away_team: str
    commence_time: datetime
    bookmaker: str
    market_type: str
    home_price: int | None
    away_price: int | None
    home_point: float | None
    total_point: float | None
    snapshot_time: datetime


class OddsFetcher:
    """Client for The Odds API."""

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url or "https://api.the-odds-api.com/v4/sports"

    def fetch_odds(self, sport_key: str) -> list[OddsSnapshotPayload]:
        """Fetch odds for a given sport key."""
        url = f"{self.base_url}/{sport_key}/odds/"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
        }
        response = _request_with_retries(url, params=params)
        if response is None:
            return []

        _log_rate_limit(response.headers)
        data = response.json()
        return _parse_odds_payloads(sport_key, data)


def _request_with_retries(url: str, params: dict[str, Any]) -> requests.Response | None:
    """Perform a GET request with exponential backoff."""
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays, start=1):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            logger.warning("Odds API request failed (attempt %s): %s", attempt, exc)
            if attempt == len(delays):
                break
            time_to_sleep = delay
            _sleep(time_to_sleep)
    return None


def _sleep(seconds: int) -> None:
    """Sleep helper to allow testing overrides."""
    import time

    time.sleep(seconds)


def _log_rate_limit(headers: dict[str, str]) -> None:
    remaining = headers.get("x-requests-remaining")
    used = headers.get("x-requests-used")
    if remaining is None and used is None:
        return
    logger.info("Odds API usage - remaining=%s used=%s", remaining, used)


def _parse_odds_payloads(
    sport_key: str, payload: list[dict[str, Any]]
) -> list[OddsSnapshotPayload]:
    snapshots: list[OddsSnapshotPayload] = []
    now = datetime.utcnow()

    for event in payload:
        commence_time = datetime.fromisoformat(
            event["commence_time"].replace("Z", "+00:00")
        )
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                market_type = market.get("key")
                home_price, away_price, home_point, total_point = _parse_market(
                    market, event
                )
                if home_price is None and away_price is None:
                    continue
                snapshots.append(
                    OddsSnapshotPayload(
                        sport_key=sport_key,
                        sport_title=event.get("sport_title", sport_key),
                        external_game_id=event["id"],
                        home_team=event["home_team"],
                        away_team=event["away_team"],
                        commence_time=commence_time,
                        bookmaker=bookmaker.get("title", bookmaker.get("key", "")),
                        market_type=market_type,
                        home_price=home_price,
                        away_price=away_price,
                        home_point=home_point,
                        total_point=total_point,
                        snapshot_time=now,
                    )
                )
    return snapshots


def _parse_market(
    market: dict[str, Any], event: dict[str, Any]
) -> tuple[int | None, int | None, float | None, float | None]:
    outcomes = market.get("outcomes", [])
    home_price = away_price = None
    home_point = total_point = None

    if market.get("key") == "totals":
        over = next((o for o in outcomes if o.get("name") == "Over"), None)
        under = next((o for o in outcomes if o.get("name") == "Under"), None)
        if over and under:
            home_price = over.get("price")
            away_price = under.get("price")
            total_point = over.get("point")
        return home_price, away_price, None, total_point

    home = next((o for o in outcomes if o.get("name") == event["home_team"]), None)
    away = next((o for o in outcomes if o.get("name") == event["away_team"]), None)
    if home and away:
        home_price = home.get("price")
        away_price = away.get("price")
        if market.get("key") == "spreads":
            home_point = home.get("point")
    return home_price, away_price, home_point, None
