"""Keeps the input state and ships it down a TCP socket to the emulator."""

import enum
import logging
import queue
import socket
import threading
import time
from typing import TYPE_CHECKING

from rich.style import Style

if TYPE_CHECKING:
    from webcontroller.config import AppConf

logger = logging.getLogger(__name__)

# Input logger, message only, so the player input scroll stays readable.
input_logger = logging.getLogger("webcontroller.input")
input_logger.propagate = False
input_logger.setLevel(logging.INFO)
_input_handler = logging.StreamHandler()
_input_handler.setFormatter(logging.Formatter("%(message)s"))
input_logger.addHandler(_input_handler)

CLIENT_TIMEOUT_S = 7  # Drop a client from the player count if it hasn't pinged in this long.
RECONNECT_DELAY_S = 1

COLOURS = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")


class Button(enum.StrEnum):
    """The buttons, declaration order is mGBA's button bitmask order, don't reorder these.

    A StrEnum rather than an IntFlag so the api takes and the OpenAPI schema documents the names, which is what
    makes the generated typescript client useful.
    """

    GBA_A = "GBA_A"
    GBA_B = "GBA_B"
    GBA_SELECT = "GBA_SELECT"
    GBA_START = "GBA_START"
    GBA_RIGHT = "GBA_RIGHT"
    GBA_LEFT = "GBA_LEFT"
    GBA_UP = "GBA_UP"
    GBA_DOWN = "GBA_DOWN"
    GBA_R = "GBA_R"
    GBA_L = "GBA_L"

    @property
    def bit(self) -> int:
        """The bit this button sets in the state sent to the emulator."""
        return 1 << list(Button).index(self)


def log_player_input(client_id: str, button: Button) -> None:
    """Log a button press with the player's coloured id."""
    input_logger.info("Player: %s %s", colour_player_id(client_id), button.name.removeprefix("GBA_"))


def colour_player_id(player_id: str) -> str:
    """Fun coloured player names, the same id always gets the same colours."""
    padded = player_id[:6].ljust(6)
    chunks = [padded[i : i + 3] for i in range(0, 6, 3)]

    coloured = ""
    for chunk in chunks:
        # Colour each chunk based on the sum of its characters, so a chunk is always coloured the same way.
        fun_number = sum(bytearray(chunk, "ascii"))
        fg_idx = (fun_number * 2) % len(COLOURS)
        bg_idx = fun_number % len(COLOURS)
        if fg_idx == bg_idx:  # Don't render a chunk invisible
            bg_idx = (bg_idx + 1) % len(COLOURS)

        # Style.render() rather than a Console, the log handler wants a plain string with the escapes already in it.
        coloured += Style(color=COLOURS[fg_idx], bgcolor=COLOURS[bg_idx], bold=True).render(chunk)

    return coloured


class Controller:
    """Current button state, connected players, and the socket sender thread."""

    def __init__(self, app_conf: AppConf) -> None:
        """Init the controller, does not start the socket sender thread."""
        self._conf = app_conf
        self._state = 0  # Bitmask of the currently held buttons, in Button declaration order.
        self._queue: queue.SimpleQueue[int] = queue.SimpleQueue()
        self._stop = threading.Event()
        self.sock_connected = False
        self.clients: dict[str, float] = {}

    # --- Input -------------------------------------------------------------

    def press(self, button: Button, *, down: bool) -> None:
        """Set/clear a button in the state and queue the new state for the emulator."""
        self._state = (self._state | button.bit) if down else (self._state & ~button.bit)
        logger.debug("Input! %s: %s -> %010b", "Down" if down else "Up", button.name, self._state)
        self._queue.put(self._state)

    # --- Players -----------------------------------------------------------

    def ping(self, client_id: str) -> None:
        """Record that a client is still around, and drop the ones that aren't."""
        now = time.monotonic()
        self.clients[client_id] = now
        self.clients = {cid: last for cid, last in self.clients.items() if now - last < CLIENT_TIMEOUT_S}

    # --- Socket sender -----------------------------------------------------

    def start(self) -> None:
        """Start the socket sender thread, unless the config says not to."""
        if not self._conf.run_socket:
            logger.warning("Not starting socket sender thread.")
            return

        logger.info("Starting socket sender thread!")
        threading.Thread(target=self._run, daemon=True, name="socket_sender").start()

    def stop(self) -> None:
        """Ask the socket sender thread to exit."""
        self._stop.set()

    def _run(self) -> None:
        """Connect to the emulator's socket and send whatever lands in the queue, reconnecting forever."""
        address = (self._conf.socket_address, self._conf.socket_port)

        while not self._stop.is_set():
            try:
                logger.info("Connecting to socket: %s:%s", *address)
                with socket.create_connection(address, timeout=RECONNECT_DELAY_S) as sock:
                    logger.info("Connected to socket!")
                    self.sock_connected = True
                    self._send_loop(sock)
            except OSError as exc:  # ConnectionRefusedError, timeouts, no route, ...
                logger.error("Socket connection failed: %s", exc)  # ruff: ignore[error-instead-of-exception] Don't want this one too noisy
            finally:
                self.sock_connected = False

            logger.info("Trying again...")
            self._stop.wait(RECONNECT_DELAY_S)

        logger.info("Socket sender stopped")

    def _send_loop(self, sock: socket.socket) -> None:
        """Drain the input queue to the socket at the configured tick rate."""
        tick = 1 / self._conf.tick_rate

        while not self._stop.wait(tick):  # The tick rate is a rate limit, don't flood the emulator.
            try:
                state = self._queue.get_nowait()
            except queue.Empty:
                continue

            try:
                sock.sendall(state.to_bytes(2, "little"))
            except OSError:  # BrokenPipeError and friends
                logger.error("Disconnected from socket, cringe")  # ruff: ignore[error-instead-of-exception] Don't want this one too noisy
                return
