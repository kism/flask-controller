from flask import Flask, render_template
import json
import time
import socket
import threading


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
    dainput = json.loads(dainput)
    message = ""
    # print(dainput)
    match dainput:
        case "A":
            print("GBA L")
            nextinput = "GBA_KEY_L"
        case "S":
            print("GBA R")
            nextinput = "GBA_KEY_R"
        case "D":
            print("GBA START")
            nextinput = "GBA_KEY_START"
        case "Z":
            print("GBA B")
            nextinput = "GBA_KEY_B"
        case "X":
            print("GBA A")
            nextinput = "GBA_KEY_A"
        case "C":
            print("GBA SELECT")
            nextinput = "GBA_KEY_SELECT"
        case "&":
            print("GBA UP")
            nextinput = "GBA_KEY_UP"
        case "(":
            print("GBA DOWN")
            nextinput = "GBA_KEY_DOWN"
        case "%":
            print("GBA LEFT")
            nextinput = "GBA_KEY_LEFT"
        case "'":
            print("GBA RIGHT")
            nextinput = "GBA_KEY_RIGHT"
        case _:
            message = "INVALID KEYPRESS, DROPPING"
            print(message)
            nextinput = ""

    return "Sent " + dainput + " " + message


def main():
    print("hello 1")
    thread = threading.Thread(target=socketSender)
    print("hello 2")
    thread.start()
    print("hello 3")
    print("hello 4")
    app.run(host="0.0.0.0")
    print("hello 5")
    thread.join()
    print("hello 6")


if __name__ == '__main__':
    main()
