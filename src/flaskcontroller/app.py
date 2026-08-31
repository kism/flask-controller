"""Flask app factory."""

import logging
from pathlib import Path

from flask import Flask, render_template

from .config import Config
from .constants import PROGRAM_NAME_WITH_FULL_VERSION
from .routers import controller as controller_router
from .services import Controller
from .utils.logger import setup_logger

logger = logging.getLogger(__name__)

DEFAULT_INSTANCE_PATH = Path.cwd() / "instance"


def create_app(config: Config | None = None, instance_path: Path | None = None) -> Flask:
    """Create and configure an instance of the Flask application.

    Args:
        config: Config to use, loaded from the instance directory if None. Handy for testing.
        instance_path: Directory that holds config.json, './instance' if None.
    """
    instance_path = Path(instance_path) if instance_path else DEFAULT_INSTANCE_PATH
    config = config or Config.load(instance_path)

    # Setup the root logger before Flask makes app.logger, so flask doesn't add a handler of its own.
    setup_logger(log_level=config.logging.level, log_path=config.logging.path)

    app = Flask(__name__, instance_path=str(instance_path.resolve()))
    app.config.from_mapping(config.flask.model_dump())

    controller = Controller(config.app)
    app.extensions["controller"] = controller
    controller.start()

    app.register_blueprint(controller_router.bp)

    # The home page, generally not worth putting in a blueprint.
    @app.get("/")
    def home() -> str:
        """Render the home page."""
        return render_template("home.html.j2", version=PROGRAM_NAME_WITH_FULL_VERSION)

    logger.info("Starting %s", PROGRAM_NAME_WITH_FULL_VERSION)
    logger.debug("Instance path is: %s", app.instance_path)

    return app
