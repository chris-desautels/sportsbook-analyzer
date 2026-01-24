import os


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///betting.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ODDS_API_KEY = os.getenv("ODDS_API_KEY")
    FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "15"))
    ARB_THRESHOLD_PERCENT = float(os.getenv("ARB_THRESHOLD_PERCENT", "1.0"))
    VALUE_THRESHOLD_PERCENT = float(os.getenv("VALUE_THRESHOLD_PERCENT", "3.0"))
    ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
    SUPPORTED_SPORTS = os.getenv(
        "SUPPORTED_SPORTS",
        "americanfootball_nfl,basketball_nba",
    ).split(",")
