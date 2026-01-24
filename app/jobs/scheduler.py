from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Iterable

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from app.models import ArbitrageOpportunity, Game, OddsSnapshot, Sport, ValueBet, db
from app.services.analyzer import MarketOdds, detect_arbitrage, detect_value_bets
from app.services.odds_fetcher import OddsFetcher


logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None
_last_fetch_time: datetime | None = None
_last_fetch_success: bool | None = None


def init_scheduler(app: Flask) -> None:
    """Initialize APScheduler and register jobs."""
    global _scheduler

    if _scheduler:
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: _fetch_and_analyze(app),
        trigger="interval",
        minutes=app.config["FETCH_INTERVAL_MINUTES"],
        id="fetch_odds",
        replace_existing=True,
    )
    scheduler.add_job(
        func=lambda: _cleanup_old_data(app),
        trigger="interval",
        days=1,
        id="cleanup_old_data",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler


def get_status() -> dict:
    """Return scheduler status information."""
    next_run_time = None
    if _scheduler:
        job = _scheduler.get_job("fetch_odds")
        next_run_time = job.next_run_time if job else None
    return {
        "last_fetch_time": _last_fetch_time.isoformat() if _last_fetch_time else None,
        "last_fetch_success": _last_fetch_success,
        "next_fetch_time": next_run_time.isoformat() if next_run_time else None,
        "scheduler_running": _scheduler is not None,
    }


def run_fetch_now(app: Flask) -> None:
    """Manually trigger an odds fetch + analysis cycle."""
    _fetch_and_analyze(app)


def _fetch_and_analyze(app: Flask) -> None:
    global _last_fetch_time, _last_fetch_success

    api_key = app.config.get("ODDS_API_KEY")
    if not api_key:
        logger.warning("Skipping odds fetch: ODDS_API_KEY missing.")
        return

    fetcher = OddsFetcher(api_key)
    try:
        snapshots: list = []
        for sport_key in app.config["SUPPORTED_SPORTS"]:
            snapshots.extend(fetcher.fetch_odds(sport_key))
        with app.app_context():
            _persist_snapshots(snapshots)
            _run_detection(app)
        _last_fetch_time = datetime.utcnow()
        _last_fetch_success = True
    except Exception:
        logger.exception("Odds fetch job failed.")
        _last_fetch_time = datetime.utcnow()
        _last_fetch_success = False


def _persist_snapshots(snapshots: Iterable) -> None:
    for payload in snapshots:
        sport = Sport.query.filter_by(key=payload.sport_key).first()
        if not sport:
            sport = Sport(key=payload.sport_key, name=payload.sport_title, active=True)
            db.session.add(sport)
            db.session.flush()

        game = Game.query.filter_by(external_id=payload.external_game_id).first()
        if not game:
            game = Game(
                sport_id=sport.id,
                external_id=payload.external_game_id,
                home_team=payload.home_team,
                away_team=payload.away_team,
                commence_time=payload.commence_time,
                completed=False,
            )
            db.session.add(game)
            db.session.flush()
        else:
            game.commence_time = payload.commence_time

        snapshot = OddsSnapshot(
            game_id=game.id,
            bookmaker=payload.bookmaker,
            market_type=payload.market_type,
            timestamp=payload.snapshot_time,
            home_price=payload.home_price,
            away_price=payload.away_price,
            home_point=payload.home_point,
            total_point=payload.total_point,
        )
        db.session.add(snapshot)

    db.session.commit()


def _run_detection(app: Flask) -> None:
    """Run arbitrage and value detection for active games."""
    threshold_arb = app.config["ARB_THRESHOLD_PERCENT"]
    threshold_value = app.config["VALUE_THRESHOLD_PERCENT"]

    games = Game.query.filter_by(completed=False).all()
    for game in games:
        odds_rows = (
            OddsSnapshot.query.filter_by(game_id=game.id)
            .order_by(OddsSnapshot.timestamp.desc())
            .all()
        )
        seen = set()
        market_odds = []
        for row in odds_rows:
            key = (row.bookmaker, row.market_type)
            if key in seen:
                continue
            seen.add(key)
            if row.home_price is None or row.away_price is None:
                continue
            market_odds.append(
                MarketOdds(
                    bookmaker=row.bookmaker,
                    market_type=row.market_type,
                    home_price=row.home_price,
                    away_price=row.away_price,
                )
            )

        arbitrage = detect_arbitrage(market_odds, threshold_arb)
        value_bets = detect_value_bets(market_odds, threshold_value)

        for opportunity in arbitrage:
            db.session.add(
                ArbitrageOpportunity(
                    game_id=game.id,
                    profit_percentage=opportunity["profit_percentage"],
                    resolved=False,
                    bet_details=opportunity["bet_details"],
                )
            )

        for value in value_bets:
            db.session.add(
                ValueBet(
                    game_id=game.id,
                    bookmaker=value["bookmaker"],
                    market_type=value["market_type"],
                    edge_percentage=value["edge_percentage"],
                    consensus_price=value["consensus_price"],
                    book_price=value["book_price"],
                )
            )

    db.session.commit()


def _cleanup_old_data(app: Flask) -> None:
    with app.app_context():
        cutoff = datetime.utcnow() - timedelta(days=30)
        deleted = OddsSnapshot.query.filter(
            OddsSnapshot.timestamp < cutoff
        ).delete()
        db.session.commit()
        logger.info("Deleted %s old odds snapshots.", deleted)
