from __future__ import annotations

import logging

from dotenv import load_dotenv

# Load .env BEFORE importing Config
load_dotenv()

from flask import Flask

from app.jobs.scheduler import init_scheduler
from app.models import db
from config import Config


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes.api import bp as api_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.games import bp as games_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(api_bp)

    if not app.config.get("TESTING") and app.config.get("ENABLE_SCHEDULER"):
        init_scheduler(app)

    if not app.config.get("TESTING"):
        if not app.config.get("SECRET_KEY"):
            raise ValueError(
                "SECRET_KEY environment variable is required. "
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )

    if not app.config.get("ODDS_API_KEY"):
        logging.getLogger(__name__).warning(
            "ODDS_API_KEY is not set; odds fetching will be disabled."
        )

    return app
