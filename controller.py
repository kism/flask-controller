from flask import Flask, render_template
import json
import time
import socket
import threading


app = Flask(__name__)       # flask app
nextinput = ""              # global nextinput


def socketSender():
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
                    time.sleep(1)
                    try:
                        message = "hello its me, your webapp"
                        print("Sending to socket: " + message)
                        s.sendall(message.encode('utf-8'))
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
            print("GB L")
        case "S":
            print("GB R")
        case "D":
            print("GB START")
        case "Z":
            print("GB A")
        case "X":
            print("GB B")
        case "C":
            print("GB SELECT")
        case "&":
            print("GB UP")
        case "(":
            print("GB DOWN")
        case "%":
            print("GB LEFT")
        case "'":
            print("GB RIGHT")
        case _:
            message = "INVALID KEYPRESS, DROPPING"
            print(message)
            dainput = ""

    nextinput = dainput

    return "Sent " + dainput + " " + message


# @app.route('/GetUserInput', methods=['GET'])
# def GetUserInput():
#     global nextinput
#     tosend = nextinput
#     nextinput = ""
#     print("sending " + tosend + " via http")
#     return tosend

# thread = threading.Thread(target=socketHandler)
# thread.daemon = True
# thread.start()

def main():
    print("hello 1")
    thread = threading.Thread(target=socketSender)
    print("hello 2")
    thread.start()
    print("hello 3")
    print("hello 4")
    app.run()
    print("hello 5")
    thread.join()
    print("hello 6")


if __name__ == '__main__':
    main()
