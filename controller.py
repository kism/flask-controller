#!/usr/bin/env python3
from flask import Flask, render_template
import argparse
import time
import socket
import threading
import logging

# "User Set"
pollingrate = 120          # Tick Rate (Outputs Per Second)
WEBADDRESS = "0.0.0.0"     # Web Interface Bind Address (0.0.0.0)
WEBPORT = 5000             # Web Interface http Port
SOCKETHOST = "127.0.0.1"   # Socket Server (mGBA) Address
SOCKETPORT = 5001          # Socket Server (mGBA) Port


log = logging.getLogger('werkzeug')  # Flask Logger
log.setLevel(logging.ERROR)
app = Flask(__name__)                # Flask app object
inputqueue = []                       # Global inputqueue, shared between threads


def socketSender(args):  # Connect to mGBA socket and send commands
    global inputqueue
    connected = False
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                connected = False
                while not connected:
                    print("Connecting to socket: " +
                          args.SOCKETHOST + ":" + str(args.SOCKETPORT))
                    try:
                        s.connect((args.SOCKETHOST, args.SOCKETPORT))
                        connected = True
                        print("Connected to socket!")
                    except ConnectionRefusedError:
                        time.sleep(1)

                while connected:
                    time.sleep(1/pollingrate)
                    try:
                        if inputqueue:
                            s.sendall(inputqueue.pop(0).encode('ascii'))

                    except BrokenPipeError:
                        print("Disconnected from socket, cringe")
                        connected = False
        except OSError:
            s = None


# Flask Home
@app.route('/')
def home():
    return render_template('home.html')


# Flask Process User Input (From Javascript)
@app.route('/ProcessUserInput/<string:dainput>', methods=['POST'])
def ProcessUserInput(dainput):
    global inputqueue
    message = ""

    validinputs = ['D_GBA_KEY_L', 'U_GBA_KEY_L', 'D_GBA_KEY_R', 'U_GBA_KEY_R', 'D_GBA_KEY_START', 'U_GBA_KEY_START', 'D_GBA_KEY_B', 'U_GBA_KEY_B', 'D_GBA_KEY_A', 'U_GBA_KEY_A',
                   'D_GBA_KEY_SELECT', 'U_GBA_KEY_SELECT', 'D_GBA_KEY_LEFT', 'U_GBA_KEY_LEFT', 'D_GBA_KEY_UP', 'U_GBA_KEY_UP', 'D_GBA_KEY_RIGHT', 'U_GBA_KEY_RIGHT', 'D_GBA_KEY_DOWN', 'U_GBA_KEY_DOWN']

    if dainput not in validinputs:
        message = "INVALID KEYPRESS, DROPPING"
    else:
        dainput = dainput.ljust(16, "_")
        message = dainput
        inputqueue.append(dainput)

    message = "Sent " + message
    print(message)
    return message


def main(args):  # Create and start thread of socketSender function, start Flask webapp
    thread = threading.Thread(target=socketSender, args=(args,))
    thread.start()
    app.run(host=args.WEBADDRESS, port=args.WEBPORT)
    thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask WebUI, Socket Sender for mGBA')
    parser.add_argument('-wa', '--webaddress', type=str, dest='WEBADDRESS',
                        help='(WebUI) Web address to listen on, default is 0.0.0.0', default="0.0.0.0")
    parser.add_argument('-wp', '--webport', type=int, dest='WEBPORT',
                        help='(WebUI) Web port to listen on, default is 5000', default=5000)
    parser.add_argument('-sa', '--socketaddress', type=str, dest='SOCKETHOST',
                        help='(mGBA) IP address that mGBA is listening on, default is 127.0.0.1', default="127.0.0.1")
    parser.add_argument('-sp', '--socketport', type=int, dest='SOCKETPORT',
                        help='(mGBA) Web port that mGBA is listening on, default is 5001', default=5001)
    parser.add_argument('--debug', dest='debug',
                        action='store_true', help='Show debug output')
    args = parser.parse_args()
    main(args)
