from datetime import datetime, timedelta

from app.jobs.scheduler import _select_fetch_interval
from app.models import Game, Sport, db


def test_select_fetch_interval_default(app):
    with app.app_context():
        interval = _select_fetch_interval(app)
        assert interval == app.config["FETCH_INTERVAL_DEFAULT_MINUTES"]


def test_select_fetch_interval_windowed(app):
    now = datetime.utcnow()
    with app.app_context():
        sport = Sport(key="basketball_nba", name="NBA", active=True)
        db.session.add(sport)
        db.session.flush()
        game = Game(
            sport_id=sport.id,
            external_id="game-windowed",
            home_team="Home",
            away_team="Away",
            commence_time=now + timedelta(hours=2),
            completed=False,
        )
        db.session.add(game)
        db.session.commit()

        interval = _select_fetch_interval(app)
        assert interval == app.config["FETCH_INTERVAL_NEAR_MINUTES"]


def test_select_fetch_interval_imminent(app):
    now = datetime.utcnow()
    with app.app_context():
        sport = Sport(key="americanfootball_nfl", name="NFL", active=True)
        db.session.add(sport)
        db.session.flush()
        game = Game(
            sport_id=sport.id,
            external_id="game-imminent",
            home_team="Home",
            away_team="Away",
            commence_time=now + timedelta(minutes=30),
            completed=False,
        )
        db.session.add(game)
        db.session.commit()

        interval = _select_fetch_interval(app)
        assert interval == app.config["FETCH_INTERVAL_IMMINENT_MINUTES"]
