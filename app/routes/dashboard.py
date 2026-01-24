from __future__ import annotations

from datetime import datetime

from flask import Blueprint, current_app, redirect, render_template, url_for

from app.jobs.scheduler import get_status, run_fetch_now
from app.models import ArbitrageOpportunity, Game, OddsSnapshot, ValueBet


bp = Blueprint("dashboard", __name__)


@bp.route("/")
def dashboard():
    status = get_status()
    arbs = (
        ArbitrageOpportunity.query.filter_by(resolved=False)
        .order_by(ArbitrageOpportunity.profit_percentage.desc())
        .limit(25)
        .all()
    )
    value_bets = (
        ValueBet.query.order_by(ValueBet.edge_percentage.desc()).limit(25).all()
    )
    upcoming_games = (
        Game.query.filter(Game.commence_time >= datetime.utcnow())
        .order_by(Game.commence_time.asc())
        .limit(20)
        .all()
    )

    odds_by_game = {
        game.id: _latest_odds_for_game(game.id) for game in upcoming_games
    }

    return render_template(
        "dashboard.html",
        status=status,
        arbitrage=arbs,
        value_bets=value_bets,
        upcoming_games=upcoming_games,
        odds_by_game=odds_by_game,
    )


@bp.post("/fetch-now")
def fetch_now():
    run_fetch_now(current_app)
    return redirect(url_for("dashboard.dashboard"))


def _latest_odds_for_game(game_id: int) -> list[OddsSnapshot]:
    snapshots = (
        OddsSnapshot.query.filter_by(game_id=game_id)
        .order_by(OddsSnapshot.timestamp.desc())
        .all()
    )
    seen = set()
    latest = []
    for snapshot in snapshots:
        key = (snapshot.bookmaker, snapshot.market_type)
        if key in seen:
            continue
        seen.add(key)
        latest.append(snapshot)
    return latest
