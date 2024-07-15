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
last_input_array = [False, False, False, False, False, False, False, False, False, False]


# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((HOST, PORT))

# Set the maximum number of queued connections
server_socket.listen(5)

logging.info("Server listening on %s:%s", HOST, PORT)


def iterate_bits(num: int) -> list:
    """Make a gross dict representing 10 bits."""
    input_array = []
    binary_representation = bin(num)[2:]  # Convert the integer to binary and remove the '0b' prefix
    binary_representation = binary_representation.zfill(10)  # Assuming 32-bit integers for illustration

    for _bit_position, bit_value in enumerate(binary_representation[::-1]):
        logger.debug("Bit at position: %s:%s", _bit_position, bit_value)
        new_bit_value = bit_value != "0"  # Why didn't I comment this, this is nonsense
        input_array.append(new_bit_value)

    return input_array


def press_buttons(in_data: bytes) -> None:
    """Bitwise compare to the socked and press/release depending."""
    global last_input_array  # noqa: PLW0603 fine for this program/scale

    my_int = int.from_bytes(in_data, "little")

    input_array = iterate_bits(my_int)

    logger.debug(str(input_array))

    logger.debug("New input: %s", int.from_bytes(in_data))
    keys = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
    n = 0

    for key in keys:
        if input_array[n] != last_input_array[n]:
            if input_array[n]:
                if DUMMY_SERVER:
                    logging.info("Pressing %s", key)
                else:
                    pydirectinput.keyDown(key)
            else:  # noqa: PLR5501 HUH?
                if DUMMY_SERVER:
                    logging.info("Releasing %s", key)
                else:
                    pydirectinput.keyUp(key)
        n = n + 1

    last_input_array = input_array


while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    logging.info("Connection from: %s", client_address)

    try:
        while True:
            # Receive and logging.info data from the client
            data = client_socket.recv(2)
            press_buttons(data)
    except Exception:
        logging.exception("Restarting Socket Client")

    # Close the connection with the client
    client_socket.close()
