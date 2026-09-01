"""Router for the controller, this is what the frontend talks to."""

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel

from webcontroller.services import Button, log_player_input

if TYPE_CHECKING:
    from webcontroller.services import Controller

logger = logging.getLogger(__name__)

router = APIRouter(tags=["controller"])

ClientId = Annotated[str, Header(alias="client-id", description="Whatever the player is calling themselves.")]


class StatusResponse(BaseModel):
    """What the frontend polls for, to render the stats table."""

    sock_connected: bool
    players_connected: int


class ButtonInput(BaseModel):
    """A keypress from the frontend."""

    button: Button
    down: bool  # True on keydown, False on keyup.


def _get_controller(request: Request) -> Controller:
    """Get the app's Controller, set in create_app()."""
    return request.app.state.controller


@router.get("/status")
def get_status(request: Request, client_id: ClientId) -> StatusResponse:
    """Status of the emulator socket and the player count.

    The frontend GETs this every few seconds, which doubles as the player count heartbeat.
    """
    controller = _get_controller(request)
    controller.ping(client_id)

    return StatusResponse(
        sock_connected=controller.sock_connected,
        players_connected=len(controller.clients),
    )


@router.post("/input", status_code=HTTPStatus.NO_CONTENT)
def post_input(request: Request, client_id: ClientId, user_input: ButtonInput) -> None:
    """Queue a button press/release from the frontend, an unknown button is a 422 from FastAPI."""
    _get_controller(request).press(user_input.button, down=user_input.down)
    if user_input.down:
        log_player_input(client_id, user_input.button)
