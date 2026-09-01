"""Blueprint for the controller, this is what the javascript talks to."""

import logging
from http import HTTPStatus
from typing import Self

from flask import Blueprint, current_app, request
from pydantic import BaseModel

from flaskcontroller.services import Button, Controller, log_player_input

logger = logging.getLogger(__name__)

bp = Blueprint("controller", __name__)


class StatusResponse(BaseModel):
    """What the javascript polls for, to render the stats table."""

    sock_connected: bool
    players_connected: int


class ButtonInput(BaseModel):
    """A keypress from the javascript, e.g. 'D_GBA_A' or 'U_GBA_START'."""

    button: Button
    down: bool

    @classmethod
    def parse(cls, raw: str) -> Self:
        """Parse the '<D|U>_<BUTTON>' string from the url, raising ValueError if it isn't one."""
        direction, _, name = raw.partition("_")
        if direction not in {"D", "U"} or name not in Button.__members__:
            msg = f"Not a valid input: {raw}"
            raise ValueError(msg)
        return cls(button=Button[name], down=direction == "D")


def _controller() -> Controller:
    """Get the app's Controller, set in create_app()."""
    return current_app.extensions["controller"]


@bp.get("/GetStatus")
def get_status() -> dict:
    """Status of the emulator socket and the player count.

    The javascript GETs this every few seconds, which doubles as the player count heartbeat.
    """
    controller = _controller()
    controller.ping(request.headers.get("client-id", ""))

    return StatusResponse(
        sock_connected=controller.sock_connected,
        players_connected=len(controller.clients),
    ).model_dump()


@bp.post("/input/<da_input>")
def process_user_input(da_input: str) -> tuple[str, int]:
    """Queue a button press/release from the javascript."""
    client_id = request.headers.get("client-id")
    if not client_id:
        return "No client ID", HTTPStatus.BAD_REQUEST

    try:
        user_input = ButtonInput.parse(da_input)
    except ValueError:
        return "INVALID KEYPRESS, DROPPING", HTTPStatus.OK

    controller = _controller()
    controller.press(user_input.button, down=user_input.down)
    if user_input.down:
        log_player_input(client_id, user_input.button)

    return "VALID KEYPRESS", HTTPStatus.OK
