from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, current_app, redirect, render_template, url_for

from app.jobs.scheduler import get_status, run_fetch_now
from app.models import ArbitrageOpportunity, Game, OddsSnapshot, PinnedGame, ValueBet, db
from app.services.odds_insights import (
    best_lines_from_snapshots,
    detect_steam_moves,
    latest_snapshots_for_game,
)


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
    pinned_games = (
        Game.query.join(PinnedGame, Game.id == PinnedGame.game_id)
        .filter(Game.commence_time >= datetime.utcnow())
        .order_by(PinnedGame.pinned_at.desc())
        .all()
    )
    pinned_ids = [game.id for game in pinned_games]
    remaining = max(0, 20 - len(pinned_games))
    unpinned_query = Game.query.filter(Game.commence_time >= datetime.utcnow())
    if pinned_ids:
        unpinned_query = unpinned_query.filter(~Game.id.in_(pinned_ids))
    unpinned_games = unpinned_query.order_by(Game.commence_time.asc()).limit(remaining).all()
    upcoming_games = pinned_games + unpinned_games

    odds_by_game = {game.id: latest_snapshots_for_game(game.id) for game in upcoming_games}
    best_lines_by_game = {
        game.id: best_lines_from_snapshots(odds_by_game[game.id])
        for game in upcoming_games
    }
    steam_moves_by_game = _steam_moves_by_game(upcoming_games)

    return render_template(
        "dashboard.html",
        status=status,
        arbitrage=arbs,
        value_bets=value_bets,
        upcoming_games=upcoming_games,
        odds_by_game=odds_by_game,
        best_lines_by_game=best_lines_by_game,
        steam_moves_by_game=steam_moves_by_game,
        pinned_ids=set(pinned_ids),
    )


@bp.post("/fetch-now")
def fetch_now():
    run_fetch_now(current_app)
    return redirect(url_for("dashboard.dashboard"))


@bp.post("/games/<int:game_id>/pin")
def pin_game(game_id: int):
    game = Game.query.get(game_id)
    if not game:
        return redirect(url_for("dashboard.dashboard"))
    existing = PinnedGame.query.filter_by(game_id=game_id).first()
    if not existing:
        db.session.add(PinnedGame(game_id=game_id))
        db.session.commit()
    return redirect(url_for("dashboard.dashboard"))


@bp.post("/games/<int:game_id>/unpin")
def unpin_game(game_id: int):
    pinned = PinnedGame.query.filter_by(game_id=game_id).first()
    if pinned:
        db.session.delete(pinned)
        db.session.commit()
    return redirect(url_for("dashboard.dashboard"))


def _steam_moves_by_game(games: list[Game]) -> dict[int, list[dict]]:
    window_minutes = current_app.config["STEAM_WINDOW_MINUTES"]
    min_books = current_app.config["STEAM_MIN_BOOKS"]
    min_price_move = current_app.config["STEAM_MIN_PRICE_MOVE"]
    min_point_move = current_app.config["STEAM_MIN_POINT_MOVE"]
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    steam_moves_by_game: dict[int, list[dict]] = {}
    for game in games:
        snapshots = (
            OddsSnapshot.query.filter_by(game_id=game.id)
            .filter(OddsSnapshot.timestamp >= cutoff)
            .order_by(OddsSnapshot.timestamp.asc())
            .all()
        )
        steam_moves_by_game[game.id] = detect_steam_moves(
            snapshots,
            window_minutes=window_minutes,
            min_books=min_books,
            min_price_move=min_price_move,
            min_point_move=min_point_move,
        )
    return steam_moves_by_game
