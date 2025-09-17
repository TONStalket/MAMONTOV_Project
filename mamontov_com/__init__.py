from __future__ import annotations

from typing import Optional, Dict, Any

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database instance shared across the application

db = SQLAlchemy()


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """Application factory for the Mamontov social network."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.config.update(
        SECRET_KEY="change-me-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///mamontov.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config:
        app.config.update(config)

    db.init_app(app)

    # Import routes lazily to avoid circular imports
    from . import routes  # noqa: WPS433

    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app


__all__ = ["create_app", "db"]
