from __future__ import annotations

from flask import Blueprint, abort, current_app, render_template

from app.models import ArbitrageOpportunity, Game, OddsSnapshot, PinnedGame, ValueBet
from app.services.odds_insights import best_lines_from_snapshots, detect_steam_moves


bp = Blueprint("games", __name__)


@bp.route("/games/<int:game_id>")
def game_detail(game_id: int):
    game = Game.query.get(game_id)
    if not game:
        abort(404)

    odds = (
        OddsSnapshot.query.filter_by(game_id=game_id)
        .order_by(OddsSnapshot.timestamp.desc())
        .all()
    )
    arbitrage = (
        ArbitrageOpportunity.query.filter_by(game_id=game_id)
        .order_by(ArbitrageOpportunity.detected_at.desc())
        .all()
    )
    value_bets = (
        ValueBet.query.filter_by(game_id=game_id)
        .order_by(ValueBet.detected_at.desc())
        .all()
    )
    best_lines = best_lines_from_snapshots(odds)
    steam_moves = detect_steam_moves(
        odds,
        window_minutes=current_app.config["STEAM_WINDOW_MINUTES"],
        min_books=current_app.config["STEAM_MIN_BOOKS"],
        min_price_move=current_app.config["STEAM_MIN_PRICE_MOVE"],
        min_point_move=current_app.config["STEAM_MIN_POINT_MOVE"],
    )
    is_pinned = PinnedGame.query.filter_by(game_id=game_id).first() is not None

    return render_template(
        "game_detail.html",
        game=game,
        odds=odds,
        arbitrage=arbitrage,
        value_bets=value_bets,
        best_lines=best_lines,
        steam_moves=steam_moves,
        is_pinned=is_pinned,
    )
