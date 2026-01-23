from datetime import datetime

from app.models import ArbitrageOpportunity, OddsSnapshot, ValueBet, db


def test_api_status(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "scheduler_running" in response.json


def test_api_games_and_history(client, app, sample_game):
    with app.app_context():
        snapshot = OddsSnapshot(
            game_id=sample_game.id,
            bookmaker="Book A",
            market_type="h2h",
            timestamp=datetime.utcnow(),
            home_price=120,
            away_price=-130,
        )
        db.session.add(snapshot)
        db.session.commit()

    games_response = client.get("/api/games")
    assert games_response.status_code == 200
    assert games_response.json

    history_response = client.get(f"/api/games/{sample_game.id}/history")
    assert history_response.status_code == 200
    assert history_response.json


def test_api_opportunities(client, app, sample_game):
    with app.app_context():
        arb = ArbitrageOpportunity(
            game_id=sample_game.id,
            profit_percentage=1.5,
            resolved=False,
            bet_details={"home": {"bookmaker": "A"}, "away": {"bookmaker": "B"}},
        )
        value = ValueBet(
            game_id=sample_game.id,
            bookmaker="Book A",
            market_type="h2h",
            edge_percentage=3.2,
            consensus_price=120,
            book_price=150,
        )
        db.session.add(arb)
        db.session.add(value)
        db.session.commit()

    response = client.get("/api/opportunities")
    assert response.status_code == 200
    payload = response.json
    assert payload["arbitrage"]
    assert payload["value_bets"]
