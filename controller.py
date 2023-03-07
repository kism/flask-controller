from flask import Flask, render_template
import json
import time
import socket
import threading
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)       # flask app
nextinput = ""              # global nextinput


def socketSender():
    global nextinput
    print("Attempting to open a socket")
    HOST = "127.0.0.1"
    PORT = 5001
    connected = False
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                connected = False
                while not connected:
                    print("Connecting to socket: " + HOST + ":" + str(PORT))
                    try:
                        s.connect((HOST, PORT))
                        connected = True
                        print("Connected to socket!")
                    except ConnectionRefusedError:
                        time.sleep(1)

                while connected:
                    time.sleep(1/60)
                    try:
                        # message = "hello its me, your webapp"
                        # print("Sending to socket: " + message)
                        if nextinput != "":
                            s.sendall(nextinput.encode('utf-8'))
                            nextinput = ""

                    except BrokenPipeError:
                        print("Disconnected from socket, cringe")
                        connected = False
        except OSError:
            s = None


# Flask
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/ProcessUserInput/<string:dainput>', methods=['POST'])
def ProcessUserInput(dainput):
    global nextinput
    message = ""

    validinputs = ['D_GBA_KEY_L', 'U_GBA_KEY_L', 'D_GBA_KEY_R', 'U_GBA_KEY_R', 'D_GBA_KEY_START', 'U_GBA_KEY_START', 'D_GBA_KEY_B', 'U_GBA_KEY_B', 'D_GBA_KEY_A', 'U_GBA_KEY_A',
                   'D_GBA_KEY_SELECT', 'U_GBA_KEY_SELECT', 'D_GBA_KEY_LEFT', 'U_GBA_KEY_LEFT', 'D_GBA_KEY_UP', 'U_GBA_KEY_UP', 'D_GBA_KEY_RIGHT', 'U_GBA_KEY_RIGHT', 'D_GBA_KEY_DOWN', 'U_GBA_KEY_DOWN']

    if dainput not in validinputs:
        message = "INVALID KEYPRESS, DROPPING"
        nextinput = ""
    else:
        message = dainput
        nextinput = dainput

    message = "Sent " + message
    print(message)
    return message


def main():
    thread = threading.Thread(target=socketSender)
    thread.start()
    app.run(host="0.0.0.0")
    thread.join()


if __name__ == '__main__':
    main()
