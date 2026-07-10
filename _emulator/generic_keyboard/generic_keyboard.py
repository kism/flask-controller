#!/usr/bin/env python3
"""Client to get the inputs and output them as key presses."""

import logging
import socket

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

DUMMY_SERVER = True

if not DUMMY_SERVER:
    import pydirectinput

    pydirectinput.PAUSE = 1 / 120

SERVER = None
HOST = "localhost"
PORT = 5001
KEYS = "qwertyuiop"
last_state = 0


# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((HOST, PORT))

# Set the maximum number of queued connections
server_socket.listen(5)

logger.info("Server listening on %s:%s", HOST, PORT)


def press_buttons(in_data: bytes) -> None:
    """Press/release keys whose bits changed since the last packet."""
    global last_state  # noqa: PLW0603 fine for this program/scale

    state = int.from_bytes(in_data, "little")
    logger.debug("New input: %010b", state)

    for n, key in enumerate(KEYS):
        bit = 1 << n
        if (state ^ last_state) & bit:  # this bit changed
            pressed = bool(state & bit)
            if DUMMY_SERVER:
                logger.info("%s %s", "Pressing" if pressed else "Releasing", key)
            elif pressed:
                pydirectinput.keyDown(key)
            else:
                pydirectinput.keyUp(key)

    last_state = state


while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    logger.info("Connection from: %s", client_address)

    try:
        while True:
            # Receive and logging.info data from the client
            data = client_socket.recv(2)
            press_buttons(data)
    except Exception:
        logger.exception("Restarting Socket Client")

    # Close the connection with the client
    client_socket.close()
