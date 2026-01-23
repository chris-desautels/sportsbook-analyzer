from __future__ import annotations

import logging

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

    if not app.config.get("TESTING"):
        init_scheduler(app)

    if not app.config.get("ODDS_API_KEY"):
        logging.getLogger(__name__).warning(
            "ODDS_API_KEY is not set; odds fetching will be disabled."
        )

    return app
