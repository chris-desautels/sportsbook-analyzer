from __future__ import annotations

from flask import Blueprint, abort, render_template

from app.models import ArbitrageOpportunity, Game, OddsSnapshot, ValueBet


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

    return render_template(
        "game_detail.html",
        game=game,
        odds=odds,
        arbitrage=arbitrage,
        value_bets=value_bets,
    )
