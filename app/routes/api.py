from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify

from app.jobs.scheduler import get_status
from app.models import ArbitrageOpportunity, Game, OddsSnapshot, ValueBet
from app.services.odds_insights import latest_snapshots_for_game


bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/opportunities")
def opportunities():
    arbs = (
        ArbitrageOpportunity.query.filter_by(resolved=False)
        .order_by(ArbitrageOpportunity.profit_percentage.desc())
        .all()
    )
    value_bets = (
        ValueBet.query.order_by(ValueBet.edge_percentage.desc()).all()
    )
    return jsonify(
        {
            "arbitrage": [
                {
                    "game_id": arb.game_id,
                    "profit_percentage": arb.profit_percentage,
                    "detected_at": arb.detected_at.isoformat(),
                    "bet_details": arb.bet_details,
                }
                for arb in arbs
            ],
            "value_bets": [
                {
                    "game_id": value.game_id,
                    "bookmaker": value.bookmaker,
                    "market_type": value.market_type,
                    "edge_percentage": value.edge_percentage,
                    "detected_at": value.detected_at.isoformat(),
                    "consensus_price": value.consensus_price,
                    "book_price": value.book_price,
                }
                for value in value_bets
            ],
        }
    )


@bp.get("/games")
def games():
    upcoming_games = (
        Game.query.filter(Game.commence_time >= datetime.utcnow())
        .order_by(Game.commence_time.asc())
        .all()
    )

    data = []
    for game in upcoming_games:
        latest_odds = latest_snapshots_for_game(game.id)
        data.append(
            {
                "id": game.id,
                "home_team": game.home_team,
                "away_team": game.away_team,
                "commence_time": game.commence_time.isoformat(),
                "odds": [
                    {
                        "bookmaker": odds.bookmaker,
                        "market_type": odds.market_type,
                        "home_price": odds.home_price,
                        "away_price": odds.away_price,
                        "home_point": odds.home_point,
                        "total_point": odds.total_point,
                        "timestamp": odds.timestamp.isoformat(),
                    }
                    for odds in latest_odds
                ],
            }
        )

    return jsonify(data)


@bp.get("/games/<int:game_id>/history")
def game_history(game_id: int):
    odds = (
        OddsSnapshot.query.filter_by(game_id=game_id)
        .order_by(OddsSnapshot.timestamp.asc())
        .all()
    )
    return jsonify(
        [
            {
                "bookmaker": snap.bookmaker,
                "market_type": snap.market_type,
                "home_price": snap.home_price,
                "away_price": snap.away_price,
                "home_point": snap.home_point,
                "total_point": snap.total_point,
                "timestamp": snap.timestamp.isoformat(),
            }
            for snap in odds
        ]
    )


@bp.get("/status")
def status():
    return jsonify(get_status())


def _latest_odds_for_game(game_id: int) -> list[OddsSnapshot]:
    return latest_snapshots_for_game(game_id)
