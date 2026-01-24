from datetime import datetime, timedelta

from app.models import OddsSnapshot, db
from app.services.odds_insights import best_lines_for_game, detect_steam_moves


def test_best_lines_for_game_uses_latest_snapshots(app, sample_game):
    now = datetime.utcnow()
    with app.app_context():
        db.session.add_all(
            [
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book A",
                    market_type="h2h",
                    timestamp=now - timedelta(minutes=10),
                    home_price=200,
                    away_price=-220,
                ),
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book A",
                    market_type="h2h",
                    timestamp=now - timedelta(minutes=1),
                    home_price=110,
                    away_price=-120,
                ),
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book B",
                    market_type="h2h",
                    timestamp=now - timedelta(minutes=2),
                    home_price=130,
                    away_price=-140,
                ),
            ]
        )
        db.session.commit()

        best_lines = best_lines_for_game(sample_game.id)
        assert best_lines["h2h"]["home"].bookmaker == "Book B"
        assert best_lines["h2h"]["home"].price == 130


def test_best_lines_for_spreads_and_totals(app, sample_game):
    now = datetime.utcnow()
    with app.app_context():
        db.session.add_all(
            [
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book A",
                    market_type="spreads",
                    timestamp=now - timedelta(minutes=1),
                    home_price=-110,
                    away_price=-110,
                    home_point=-3.5,
                ),
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book B",
                    market_type="spreads",
                    timestamp=now - timedelta(minutes=1),
                    home_price=-105,
                    away_price=-115,
                    home_point=-4.0,
                ),
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book A",
                    market_type="totals",
                    timestamp=now - timedelta(minutes=1),
                    home_price=-110,
                    away_price=-110,
                    total_point=48.5,
                ),
                OddsSnapshot(
                    game_id=sample_game.id,
                    bookmaker="Book B",
                    market_type="totals",
                    timestamp=now - timedelta(minutes=1),
                    home_price=-105,
                    away_price=-115,
                    total_point=49.0,
                ),
            ]
        )
        db.session.commit()

        best_lines = best_lines_for_game(sample_game.id)
        spreads = best_lines["spreads"]
        assert spreads["home"].bookmaker == "Book B"
        assert spreads["home"].price == -105
        assert spreads["home"].point == -4.0
        assert spreads["away"].bookmaker == "Book A"
        assert spreads["away"].price == -110
        assert spreads["away"].point == 3.5

        totals = best_lines["totals"]
        assert totals["over"].bookmaker == "Book B"
        assert totals["over"].price == -105
        assert totals["over"].point == 49.0
        assert totals["under"].bookmaker == "Book A"
        assert totals["under"].price == -110
        assert totals["under"].point == 48.5


def test_detect_steam_moves_price(app, sample_game):
    now = datetime.utcnow()
    snapshots = []
    for book in ("Book A", "Book B", "Book C"):
        snapshots.append(
            OddsSnapshot(
                game_id=sample_game.id,
                bookmaker=book,
                market_type="h2h",
                timestamp=now - timedelta(minutes=12),
                home_price=100,
                away_price=-110,
            )
        )
        snapshots.append(
            OddsSnapshot(
                game_id=sample_game.id,
                bookmaker=book,
                market_type="h2h",
                timestamp=now - timedelta(minutes=2),
                home_price=130,
                away_price=-140,
            )
        )

    steam_moves = detect_steam_moves(
        snapshots,
        window_minutes=15,
        min_books=3,
        min_price_move=20,
        min_point_move=0.5,
    )
    assert any(
        move["market_type"] == "h2h"
        and move["side"] == "home"
        and move["direction"] == "up"
        for move in steam_moves
    )


def test_detect_steam_moves_respects_thresholds():
    now = datetime.utcnow()
    snapshots = []
    for book in ("Book A", "Book B", "Book C"):
        snapshots.append(
            OddsSnapshot(
                game_id=1,
                bookmaker=book,
                market_type="h2h",
                timestamp=now - timedelta(minutes=10),
                home_price=100,
                away_price=-110,
            )
        )
        snapshots.append(
            OddsSnapshot(
                game_id=1,
                bookmaker=book,
                market_type="h2h",
                timestamp=now - timedelta(minutes=2),
                home_price=115,
                away_price=-110,
            )
        )

    steam_moves = detect_steam_moves(
        snapshots,
        window_minutes=15,
        min_books=3,
        min_price_move=20,
        min_point_move=0.5,
    )
    assert steam_moves == []

    snapshots.append(
        OddsSnapshot(
            game_id=1,
            bookmaker="Book D",
            market_type="h2h",
            timestamp=now - timedelta(minutes=10),
            home_price=100,
            away_price=-110,
        )
    )
    snapshots.append(
        OddsSnapshot(
            game_id=1,
            bookmaker="Book D",
            market_type="h2h",
            timestamp=now - timedelta(minutes=2),
            home_price=130,
            away_price=-110,
        )
    )

    steam_moves = detect_steam_moves(
        snapshots,
        window_minutes=15,
        min_books=3,
        min_price_move=20,
        min_point_move=0.5,
    )
    assert any(move["side"] == "home" for move in steam_moves)
