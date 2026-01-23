from datetime import datetime

import pytest

from app import create_app
from app.models import Game, Sport, db


@pytest.fixture()
def app():
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "ODDS_API_KEY": "test",
        }
    )
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sample_game(app):
    with app.app_context():
        sport = Sport(key="americanfootball_nfl", name="NFL", active=True)
        db.session.add(sport)
        db.session.flush()
        game = Game(
            sport_id=sport.id,
            external_id="game-1",
            home_team="Home",
            away_team="Away",
            commence_time=datetime(2030, 1, 1, 0, 0, 0),
            completed=False,
        )
        db.session.add(game)
        db.session.commit()
        return game
