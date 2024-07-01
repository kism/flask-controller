"""Flask webapp that interfaces with mGBA with _emulator/gba_grabwebinput.lua."""

import socket
import threading
import time

from flask import Blueprint, Flask, Response, jsonify, request

from . import get_flaskcontroller_settings

fc_sett = get_flaskcontroller_settings()

HASCOLORAMA = True
try:
    from colorama import Back, Fore, Style, init

    fgcolours = [
        Fore.BLACK,
        Fore.RED,
        Fore.GREEN,
        Fore.YELLOW,
        Fore.BLUE,
        Fore.MAGENTA,
        Fore.CYAN,
        Fore.WHITE,
    ]
    bgcolours = [
        Back.BLACK,
        Back.RED,
        Back.GREEN,
        Back.YELLOW,
        Back.BLUE,
        Back.MAGENTA,
        Back.CYAN,
        Back.WHITE,
    ]
except ImportError:
    HASCOLORAMA = False

init()

inputqueue = []
clientdict = {}

app = Flask(__name__)  # Flask app object


class FlaskWebController:
    """Object definition for the status of the socket."""

    def __init__(self) -> None:
        """Init."""
        self.current_input = 0
        self.sock_connected = False

    def get_current_input(self) -> int:
        """Get whether socket is connected."""
        return self.current_input

    def set_current_input(self, new_input: int) -> None:
        """Set current input."""
        self.current_input = new_input

    def get_sock_connected(self) -> bool:
        """Get whether socket is connected."""
        return self.sock_connected

    def set_sock_connected(self) -> None:
        """Get whether socket is connected."""
        self.sock_connected = True

    def set_sock_disconnected(self) -> None:
        """Get whether socket is connected."""
        self.sock_connected = False


bp = Blueprint("flaskcontroller", __name__)


@bp.route("/GetStatus", methods=["GET"])
def get_status() -> Response:
    """Return the status of the app."""
    # This is a 'ping' of sorts uesd to handle the playercount metric.
    # The js GETs this every x seonds.
    # The clientdict is a dictionary that stores the client-ids and when they last pinged.
    # Add current clients client id to the queue
    currenttime = int(time.time())
    clientdict.update({request.headers.get("client-id"): int(time.time())})
    for ipaddress in clientdict.copy():
        # if host hasnt been in contact in 7 seconds, drop it
        if currenttime - 7 > clientdict[ipaddress]:
            del clientdict[ipaddress]

    # Also returns the status of the mGBA socket connection
    result = {"sockconnected": fwcontroller.get_sock_connected(), "playersconnected": len(clientdict)}
    return jsonify(result)


@bp.route("/input/<string:dainput>", methods=["POST"])
def process_user_input(dainput: str) -> str:
    """Flask Process User Input (From Javascript)."""
    message = ""

    # Valid GB Button states passed from the js
    validinputs = [
        "D_GBA_L",
        "U_GBA_L",
        "D_GBA_R",
        "U_GBA_R",
        "D_GBA_START",
        "U_GBA_START",
        "D_GBA_B",
        "U_GBA_B",
        "D_GBA_A",
        "U_GBA_A",
        "D_GBA_SELECT",
        "U_GBA_SELECT",
        "D_GBA_LEFT",
        "U_GBA_LEFT",
        "D_GBA_UP",
        "U_GBA_UP",
        "D_GBA_RIGHT",
        "U_GBA_RIGHT",
        "D_GBA_DOWN",
        "U_GBA_DOWN",
    ]

    # This matches up with the button codes in mGBA
    buttoncodedict = {
        "GBA_A": 1,
        "GBA_B": 2,
        "GBA_SELECT": 4,
        "GBA_START": 8,
        "GBA_RIGHT": 16,
        "GBA_LEFT": 32,
        "GBA_UP": 64,
        "GBA_DOWN": 128,
        "GBA_R": 256,
        "GBA_L": 512,
    }

    if dainput not in validinputs:
        message = "INVALID KEYPRESS, DROPPING"
    else:
        newinput = fwcontroller.get_current_input()
        if dainput[:2] == "D_":
            # print("Input! Down: " + dainput[2:])
            newinput = newinput | buttoncodedict[dainput[2:]]
        elif dainput[:2] == "U_":
            # print("Input! Up: " + dainput[2:])
            newinput = newinput & ~(buttoncodedict[dainput[2:]])

        else:
            print("How did we get here?")

        fwcontroller.set_current_input(newinput)

        # print input as bytes
        # print("{0:b}".format(buttoncodedict[dainput[2:]]).rjust(10, '0'))
        # print("{0:b}".format(currentinput).rjust(10, '0'))

        inputqueue.append(fwcontroller.get_current_input())

        # Save some latency and do this last
        message = "VALID KEYPRESS"
        playeridcoloured = colour_player_id(request.headers.get("client-id"))

        if "D_GBA_" in dainput:
            print("Player: " + playeridcoloured + " " + dainput.replace("D_GBA_", ""))

    return message, 200


def socket_sender() -> None:
    """Connect to mGBA socket and send commands."""
    fwcontroller.set_sock_disconnected()
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                fwcontroller.set_sock_disconnected()
                while not fwcontroller.get_sock_connected():
                    print("Connecting to socket: " + fc_sett.socket_address + ":" + str(fc_sett.socket_port))
                    try:
                        sock.connect((fc_sett.socket_address, fc_sett.socket_port))
                        fwcontroller.set_sock_connected()
                        print("Connected to socket!")
                    except ConnectionRefusedError:
                        time.sleep(1)

                # While the socket between this program and mGBA is connected
                # we check to see if there is anything in the input queue
                # and then send it if there is. This runs at approximately the
                # tick rate defined. It doesnt take into consideration the processing
                # time of this block of code lol.
                while fwcontroller.get_sock_connected():
                    time.sleep(1 / fc_sett.tick_rate)
                    try:
                        if inputqueue:
                            ininput = inputqueue.pop(0).to_bytes(2, "little", signed=False)
                            sock.sendall(ininput)

                    except BrokenPipeError:
                        print("Disconnected from socket, cringe")
                        fwcontroller.set_sock_disconnected()
        except OSError:
            sock = None


def colour_player_id(playerid: str) -> str:
    """Fun coloured player names."""
    playerid = playerid[:6]
    playerid = playerid.ljust(6, " ")

    if HASCOLORAMA:  # If we have colourama installed (pip)
        newplayerid = ""
        splitplayerid = [""]

        # Split the player id string into chunks of 3
        for idx, i in enumerate(playerid):
            splitplayerid[len(splitplayerid) - 1] = splitplayerid[len(splitplayerid) - 1] + i
            if (idx + 1) % 3 == 0:
                splitplayerid.append("")

        # Colour each chunk based on the sum of its characters
        # Uses modulus of the length of the colour array
        # So each string chunk will be coloured the same way
        for i in splitplayerid:
            funnumber = sum(bytearray(i, "ascii"))
            fgpick = fgcolours[(funnumber + funnumber) % len(fgcolours)]
            bgpick = bgcolours[(funnumber) % len(bgcolours)]

            if fgcolours.index(fgpick) == bgcolours.index(bgpick):
                if bgpick == bgcolours[len(bgcolours) - 1]:
                    bgpick = bgcolours[0]
                else:
                    bgpick = bgcolours[bgcolours.index(bgpick) + 1]

            newplayerid = newplayerid + (Style.BRIGHT + fgpick + bgpick + i + Style.RESET_ALL)

        playerid = newplayerid

    return playerid


fwcontroller = FlaskWebController()

thread = threading.Thread(target=socket_sender)
thread.start()
