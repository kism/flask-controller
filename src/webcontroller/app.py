"""FastAPI app factory."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import Config
from .constants import PROGRAM_NAME, PROGRAM_NAME_WITH_FULL_VERSION
from .routers import controller as controller_router
from .services import Controller
from .utils.logger import setup_logger

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
DEFAULT_INSTANCE_PATH = Path.cwd() / "instance"

templates = Jinja2Templates(directory=HERE / "templates")


def create_app(config: Config | None = None, instance_path: Path | None = None) -> FastAPI:
    """Create and configure an instance of the FastAPI application.

    Args:
        config: Config to use, loaded from the instance directory if None. Handy for testing.
        instance_path: Directory that holds config.json, './instance' if None.
    """
    instance_path = Path(instance_path) if instance_path else DEFAULT_INSTANCE_PATH
    config = config or Config.load(instance_path)

    setup_logger(log_level=config.logging.level, log_path=config.logging.path)

    app = FastAPI(
        title=PROGRAM_NAME,
        version=PROGRAM_NAME_WITH_FULL_VERSION,
        # Operation ids are the route function names, FastAPI's default ids ('get_status_status_get') would generate
        # equally ugly names in the typescript client.
        generate_unique_id_function=lambda route: route.name,
    )
    app.state.config = config
    app.state.instance_path = instance_path

    controller = Controller(config.app)
    app.state.controller = controller
    controller.start()

    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    app.include_router(controller_router.router)

    # The home page, generally not worth putting in a router.
    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        """Render the home page."""
        return templates.TemplateResponse(
            request=request,
            name="home.html.j2",
            context={"version": PROGRAM_NAME_WITH_FULL_VERSION},
        )

    logger.info("Starting %s", PROGRAM_NAME_WITH_FULL_VERSION)
    logger.debug("Instance path is: %s", instance_path)

    return app
