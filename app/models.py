from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Sport(db.Model):
    __tablename__ = "sports"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    games = db.relationship("Game", back_populates="sport", lazy=True)

    def __repr__(self) -> str:
        return f"<Sport {self.key}>"


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"), nullable=False)
    external_id = db.Column(db.String(200), unique=True, nullable=False)
    home_team = db.Column(db.String(200), nullable=False)
    away_team = db.Column(db.String(200), nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    sport = db.relationship("Sport", back_populates="games")
    odds_snapshots = db.relationship(
        "OddsSnapshot", back_populates="game", lazy=True, cascade="all, delete-orphan"
    )
    arbitrage_opportunities = db.relationship(
        "ArbitrageOpportunity",
        back_populates="game",
        lazy=True,
        cascade="all, delete-orphan",
    )
    value_bets = db.relationship(
        "ValueBet", back_populates="game", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Game {self.external_id}>"


class OddsSnapshot(db.Model):
    __tablename__ = "odds_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    bookmaker = db.Column(db.String(120), nullable=False)
    market_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    home_price = db.Column(db.Integer, nullable=True)
    away_price = db.Column(db.Integer, nullable=True)
    home_point = db.Column(db.Float, nullable=True)
    total_point = db.Column(db.Float, nullable=True)

    game = db.relationship("Game", back_populates="odds_snapshots")

    __table_args__ = (
        db.Index("ix_odds_snapshots_game_market", "game_id", "market_type"),
        db.Index("ix_odds_snapshots_timestamp", "timestamp"),
    )


class ArbitrageOpportunity(db.Model):
    __tablename__ = "arbitrage_opportunities"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    profit_percentage = db.Column(db.Float, nullable=False)
    resolved = db.Column(db.Boolean, default=False, nullable=False)
    bet_details = db.Column(db.JSON, nullable=False)

    game = db.relationship("Game", back_populates="arbitrage_opportunities")


class ValueBet(db.Model):
    __tablename__ = "value_bets"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    bookmaker = db.Column(db.String(120), nullable=False)
    market_type = db.Column(db.String(50), nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    edge_percentage = db.Column(db.Float, nullable=False)
    consensus_price = db.Column(db.Integer, nullable=False)
    book_price = db.Column(db.Integer, nullable=False)

    game = db.relationship("Game", back_populates="value_bets")

    __table_args__ = (db.Index("ix_value_bets_game_market", "game_id", "market_type"),)


class PinnedGame(db.Model):
    __tablename__ = "pinned_games"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False, unique=True)
    pinned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    game = db.relationship("Game", backref=db.backref("pin", uselist=False))
