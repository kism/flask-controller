from flask import Flask, render_template
import json
import uinput
import time

controller = uinput.Device([
        uinput.BTN_A,
        uinput.BTN_B,
        uinput.BTN_TL,
        uinput.BTN_TR,
        uinput.BTN_START,
        uinput.BTN_SELECT,
        uinput.BTN_DPAD_UP,
        uinput.BTN_DPAD_DOWN,
        uinput.BTN_DPAD_LEFT,
        uinput.BTN_DPAD_RIGHT,
        ])

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ProcessUserInput/<string:dainput>', methods=['POST'])
def ProcessUserInput(dainput):
    dainput = json.loads(dainput)
    #print(dainput)
    match dainput:
        case "A":
            print("GB L")
            controller.emit(uinput.BTN_TL, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_TL, 0)
        case "S":
            print("GB R")
            controller.emit(uinput.BTN_TR, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_TR, 0)
        case "D":
            print("GB START")
            controller.emit(uinput.BTN_START, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_START, 0)
        case "Z":
            print("GB A")
            controller.emit(uinput.KEY_Z, 1)
            time.sleep(0.1)
            controller.emit(uinput.KEY_Z, 0)
        case "X":
            print("GB B")
            controller.emit(uinput.KEY_X, 1)
            time.sleep(0.1)
            controller.emit(uinput.KEY_X, 0)
        case "C":
            print("GB SELECT")
            controller.emit(uinput.BTN_SELECT, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_SELECT, 0)
        case "&":
            print("GB UP")
            controller.emit(uinput.BTN_DPAD_UP, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_DPAD_UP, 0)
        case "(":
            print("GB DOWN")
            controller.emit(uinput.BTN_DPAD_DOWN, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_DPAD_DOWN, 0)
        case "%":
            print("GB LEFT")
            controller.emit(uinput.BTN_DPAD_LEFT, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_DPAD_LEFT, 0)
        case "'":
            print("GB RIGHT")
            controller.emit(uinput.BTN_DPAD_RIGHT, 1)
            time.sleep(0.1)
            controller.emit(uinput.BTN_DPAD_RIGHT, 0)

        case _:
            pass

    return ""


if __name__ == '__main__':
    app.run()
