import os


class Config:
    """Application configuration loaded from environment variables."""

    # SECRET_KEY must be set via environment variable or test config
    # Generate one with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///betting.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ODDS_API_KEY = os.getenv("ODDS_API_KEY")
    FETCH_INTERVAL_DEFAULT_MINUTES = int(
        os.getenv("FETCH_INTERVAL_DEFAULT_MINUTES", os.getenv("FETCH_INTERVAL_MINUTES", "60"))
    )
    FETCH_INTERVAL_NEAR_HOURS = float(os.getenv("FETCH_INTERVAL_NEAR_HOURS", "3"))
    FETCH_INTERVAL_NEAR_MINUTES = int(os.getenv("FETCH_INTERVAL_NEAR_MINUTES", "15"))
    FETCH_INTERVAL_IMMINENT_HOURS = float(os.getenv("FETCH_INTERVAL_IMMINENT_HOURS", "1"))
    FETCH_INTERVAL_IMMINENT_MINUTES = int(
        os.getenv("FETCH_INTERVAL_IMMINENT_MINUTES", "5")
    )
    ARB_THRESHOLD_PERCENT = float(os.getenv("ARB_THRESHOLD_PERCENT", "1.0"))
    VALUE_THRESHOLD_PERCENT = float(os.getenv("VALUE_THRESHOLD_PERCENT", "3.0"))
    ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
    SUPPORTED_SPORTS = os.getenv(
        "SUPPORTED_SPORTS",
        "americanfootball_nfl,basketball_nba",
    ).split(",")
    STEAM_WINDOW_MINUTES = int(os.getenv("STEAM_WINDOW_MINUTES", "15"))
    STEAM_MIN_BOOKS = int(os.getenv("STEAM_MIN_BOOKS", "3"))
    STEAM_MIN_PRICE_MOVE = int(os.getenv("STEAM_MIN_PRICE_MOVE", "20"))
    STEAM_MIN_POINT_MOVE = float(os.getenv("STEAM_MIN_POINT_MOVE", "0.5"))