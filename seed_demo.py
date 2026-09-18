# Demo DB seed — committed so it can run on Render at boot (see render.yaml).
#
# This file used to be `_private_demo_seed.py` (gitignored, CLI-only). It is
# now committed because Render's free tier has an ephemeral filesystem: the
# SQLite DB is wiped on every cold start / redeploy / spin-down, so the demo
# deployment must reseed itself from a file that actually ships in the repo.
#
# SAFETY GATES (why a real deploy can't accidentally seed fake data)
# --------------------------------------------------------------------
# 1. This script is a no-op unless DEMO_MODE=true is set in the environment.
#    A production deploy that never sets DEMO_MODE never touches the DB here.
# 2. If DEMO_MODE=true but ENABLE_SCHEDULER=true is also set, the script
#    refuses to run (exit 1) instead of mixing demo rows with live
#    Odds-API-fetched rows. `app/__init__.py` also force-disables the
#    scheduler whenever DEMO_MODE=true, as a second, independent guard.
#
# HOW TO RUN LOCALLY (for UI testing with no Odds API key)
# ----------------------------------------------------------------------------
# From the project root, with the same virtualenv and environment files you use
# for the Flask app (e.g. `.env` with `SECRET_KEY` and `DEMO_MODE=true`):
#
#   python seed_demo.py
#
# Then start the app the normal way for this repo (e.g. `python run.py` or your
# usual command). Open `/` and `/games/<id>` in the browser.
#
# **Use the same database as a normal app run.** This script calls `create_app()`
# with no test overrides, so `load_dotenv()`, `Config`, and `SQLALCHEMY_DATABASE_URI`
# (default `sqlite:///betting.db` when `DATABASE_URL` is unset) match the running app.
# Run the seed before starting the app, or restart the app after seeding, so both
# processes see the same file/DB.
#
# HOW IT RUNS ON RENDER
# ----------------------------------------------------------------------------
# render.yaml overrides the container start command to run this script and
# then start gunicorn: `python seed_demo.py && gunicorn ...`. Every cold
# start re-runs this script against the fresh (wiped) SQLite file before the
# app starts serving traffic.
#
# RE-RUNNABLE / NO DUPLICATES
# ---------------------------
# Before inserting, all rows tied to this seed are removed: every `Game` whose
# `external_id` starts with `__private_demo_seed__` is deleted first (ORM delete
# cascades to `OddsSnapshot`, `ArbitrageOpportunity`, and `ValueBet` for that game),
# then every `Sport` whose `key` starts with the same prefix. A second run replaces
# the demo slice only; it does not empty non-demo data or hit unique constraints.

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

from app import create_app
from app.models import ArbitrageOpportunity, Game, OddsSnapshot, Sport, ValueBet, db

DEMO_PREFIX = "__private_demo_seed__"


def _clear_demo_slice() -> None:
    games = (
        Game.query.filter(Game.external_id.startswith(DEMO_PREFIX)).order_by(Game.id.asc()).all()
    )
    for game in games:
        db.session.delete(game)
    sports = Sport.query.filter(Sport.key.startswith(DEMO_PREFIX)).order_by(Sport.id.asc()).all()
    for sport in sports:
        db.session.delete(sport)
    db.session.flush()


def _seed() -> None:
    now = datetime.utcnow()
    commence_a = now + timedelta(days=2, hours=3)
    commence_b = now + timedelta(days=3, hours=1)

    sport_nba = Sport(
        key=f"{DEMO_PREFIX}nba",
        name="Basketball (Demo)",
        active=True,
    )
    sport_nfl = Sport(
        key=f"{DEMO_PREFIX}nfl",
        name="Football (Demo)",
        active=True,
    )
    db.session.add_all([sport_nba, sport_nfl])
    db.session.flush()

    game_a = Game(
        sport_id=sport_nba.id,
        external_id=f"{DEMO_PREFIX}game_lakers_celtics",
        home_team="Los Angeles Lakers",
        away_team="Boston Celtics",
        commence_time=commence_a,
        completed=False,
    )
    game_b = Game(
        sport_id=sport_nfl.id,
        external_id=f"{DEMO_PREFIX}game_bills_chiefs",
        home_team="Buffalo Bills",
        away_team="Kansas City Chiefs",
        commence_time=commence_b,
        completed=False,
    )
    db.session.add_all([game_a, game_b])
    db.session.flush()

    # Steam (h2h): default STEAM_WINDOW_MINUTES=15, STEAM_MIN_BOOKS=3,
    # STEAM_MIN_PRICE_MOVE=20 — three books with coordinated home_price moves.
    t_early = now - timedelta(minutes=14)
    t_late = now - timedelta(minutes=2)

    steam_h2h = [
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="DraftKings",
            market_type="h2h",
            timestamp=t_early,
            home_price=100,
            away_price=-120,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="DraftKings",
            market_type="h2h",
            timestamp=t_late,
            home_price=125,
            away_price=-145,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="FanDuel",
            market_type="h2h",
            timestamp=t_early,
            home_price=102,
            away_price=-118,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="FanDuel",
            market_type="h2h",
            timestamp=t_late,
            home_price=130,
            away_price=-142,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="BetMGM",
            market_type="h2h",
            timestamp=t_early,
            home_price=105,
            away_price=-125,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="BetMGM",
            market_type="h2h",
            timestamp=t_late,
            home_price=135,
            away_price=-155,
        ),
        # Extra book: latest only (best-line variety; not enough snapshots for steam)
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="Caesars",
            market_type="h2h",
            timestamp=t_late,
            home_price=128,
            away_price=-140,
        ),
    ]

    spreads_totals_a = [
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="DraftKings",
            market_type="spreads",
            timestamp=t_late,
            home_price=-110,
            away_price=-110,
            home_point=-4.5,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="FanDuel",
            market_type="spreads",
            timestamp=t_late,
            home_price=-105,
            away_price=-115,
            home_point=-5.0,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="DraftKings",
            market_type="totals",
            timestamp=t_late,
            home_price=-110,
            away_price=-110,
            total_point=224.5,
        ),
        OddsSnapshot(
            game_id=game_a.id,
            bookmaker="FanDuel",
            market_type="totals",
            timestamp=t_late,
            home_price=-108,
            away_price=-112,
            total_point=225.0,
        ),
    ]

    game_b_odds = [
        OddsSnapshot(
            game_id=game_b.id,
            bookmaker="DraftKings",
            market_type="h2h",
            timestamp=now - timedelta(minutes=5),
            home_price=-105,
            away_price=-115,
        ),
        OddsSnapshot(
            game_id=game_b.id,
            bookmaker="FanDuel",
            market_type="h2h",
            timestamp=now - timedelta(minutes=5),
            home_price=-108,
            away_price=-112,
        ),
    ]

    db.session.add_all(steam_h2h + spreads_totals_a + game_b_odds)

    arb_a = ArbitrageOpportunity(
        game_id=game_a.id,
        detected_at=now - timedelta(hours=1),
        profit_percentage=2.35,
        resolved=False,
        bet_details={
            "home": {"bookmaker": "DraftKings", "price": -105},
            "away": {"bookmaker": "FanDuel", "price": 118},
        },
    )
    arb_b = ArbitrageOpportunity(
        game_id=game_b.id,
        detected_at=now - timedelta(minutes=30),
        profit_percentage=1.85,
        resolved=False,
        bet_details={
            "home": {"bookmaker": "DraftKings", "price": 145},
            "away": {"bookmaker": "FanDuel", "price": -125},
        },
    )
    db.session.add_all([arb_a, arb_b])

    value_rows = [
        ValueBet(
            game_id=game_a.id,
            bookmaker="BetMGM",
            market_type="h2h",
            detected_at=now - timedelta(hours=2),
            edge_percentage=4.2,
            consensus_price=-108,
            book_price=-102,
        ),
        ValueBet(
            game_id=game_a.id,
            bookmaker="Caesars",
            market_type="spreads",
            detected_at=now - timedelta(hours=1),
            edge_percentage=3.5,
            consensus_price=-110,
            book_price=-105,
        ),
        ValueBet(
            game_id=game_b.id,
            bookmaker="DraftKings",
            market_type="h2h",
            detected_at=now - timedelta(minutes=45),
            edge_percentage=5.1,
            consensus_price=-112,
            book_price=-105,
        ),
    ]
    db.session.add_all(value_rows)


def main() -> None:
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    if not demo_mode:
        print(
            "DEMO_MODE is not set to 'true'; skipping demo seed (this is expected "
            "for a normal, non-demo run). Set DEMO_MODE=true to seed demo data.",
            file=sys.stderr,
        )
        return

    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        print(
            "Refusing to seed demo data: ENABLE_SCHEDULER=true would let the "
            "background job mix live Odds API rows with seeded demo rows. "
            "Set ENABLE_SCHEDULER=false (or unset it) alongside DEMO_MODE=true.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        app = create_app()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    with app.app_context():
        _clear_demo_slice()
        _seed()
        db.session.commit()

    print(
        "Demo seed complete. Start (or restart) the app from this project with the "
        "same working directory and env so it uses the same database."
    )


if __name__ == "__main__":
    main()
