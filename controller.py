#!/usr/bin/env python3
"""Flask webapp that interfaces with mGBA with _emulator/gba_grabwebinput.lua"""

# pylint: disable=global-statement

import argparse
import time
import socket
import threading
import logging

from flask import Flask, render_template, request, jsonify

inputqueue = []
clientdict = {}
CURRENTINPUT = 0
SOCKCONNECTED = False
app = Flask(__name__)  # Flask app object


def socket_sender():
    """Connect to mGBA socket and send commands"""
    global SOCKCONNECTED
    SOCKCONNECTED = False
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                SOCKCONNECTED = False
                while not SOCKCONNECTED:
                    print(
                        "Connecting to socket: "
                        + args.SOCKETHOST
                        + ":"
                        + str(args.SOCKETPORT)
                    )
                    try:
                        sock.connect((args.SOCKETHOST, args.SOCKETPORT))
                        SOCKCONNECTED = True
                        print("Connected to socket!")
                    except ConnectionRefusedError:
                        time.sleep(1)

                while SOCKCONNECTED:
                    time.sleep(1 / args.TICKRATE)
                    try:
                        if inputqueue:
                            # print("Input Queue: ", end='')
                            # for i in inputqueue:
                            #     print(i, end=' ')
                            # print()
                            # print("sending " + str(input))
                            ininput = inputqueue.pop(0).to_bytes(
                                2, "little", signed=False
                            )
                            sock.sendall(ininput)

                    except BrokenPipeError:
                        print("Disconnected from socket, cringe")
                        SOCKCONNECTED = False
        except OSError:
            sock = None


@app.route("/")
def home():
    """Flask Home"""
    return render_template("home.html")


@app.route("/GetStatus", methods=["GET"])
def get_status():
    """Return the status of the app"""
    # Add current clients client id to the queue
    currenttime = int(time.time())
    clientdict.update({request.headers.get("client-id"): int(time.time())})
    for ipaddress in clientdict.copy():  # if host hasnt been in contact in 7 seconds, drop it
        if currenttime - 7 > clientdict[ipaddress]:
            del clientdict[ipaddress]

    result = {"sockconnected": SOCKCONNECTED, "playersconnected": len(clientdict)}
    return jsonify(result)


@app.route("/input/<string:dainput>", methods=["POST"])
def process_user_input(dainput):
    """Flask Process User Input (From Javascript)"""
    global CURRENTINPUT
    message = ""

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
        print("Player: " + request.headers.get("client-id") + " " + dainput)
        message = "VALID KEYPRESS"
        if dainput[:2] == "D_":
            # print("Input! Down: " + dainput[2:])
            CURRENTINPUT = CURRENTINPUT | buttoncodedict[dainput[2:]]
        elif dainput[:2] == "U_":
            # print("Input! Up: " + dainput[2:])
            CURRENTINPUT = CURRENTINPUT & ~(buttoncodedict[dainput[2:]])
        else:
            print("How did we get here?")

        # print input as bytes
        # print("{0:b}".format(buttoncodedict[dainput[2:]]).rjust(10, '0'))
        # print("{0:b}".format(currentinput).rjust(10, '0'))

        inputqueue.append(CURRENTINPUT)

    # print(message)
    return message, 200


def main():
    """Create and start thread of socketSender function, start Flask webapp"""
    thread = threading.Thread(target=socket_sender)
    thread.start()
    app.run(host=args.WEBADDRESS, port=args.WEBPORT)
    thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask WebUI, Socket Sender for mGBA")
    parser.add_argument(
        "-wa",
        "--webaddress",
        type=str,
        dest="WEBADDRESS",
        help="(WebUI) Web address to listen on, default is 0.0.0.0",
        default="0.0.0.0",
    )
    parser.add_argument(
        "-wp",
        "--webport",
        type=int,
        dest="WEBPORT",
        help="(WebUI) Web port to listen on, default is 5000",
        default=5000,
    )
    parser.add_argument(
        "-sa",
        "--socketaddress",
        type=str,
        dest="SOCKETHOST",
        help="(mGBA) IP address that mGBA is listening on, default is 127.0.0.1",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-sp",
        "--socketport",
        type=int,
        dest="SOCKETPORT",
        help="(mGBA) Web port that mGBA is listening on, default is 5001",
        default=5001,
    )
    parser.add_argument(
        "-tr",
        "--tickrate",
        type=int,
        dest="TICKRATE",
        help="Inputs per second sent to mGBA, default is 60",
        default=120,
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Show debug output"
    )
    args = parser.parse_args()

    # Flask Logger
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    if args.debug:
        log.setLevel(logging.DEBUG)

    main()
