from flask import Flask, render_template
import json
import uinput

controller = uinput.Device([
        uinput.KEY_A,
        uinput.KEY_S,
        uinput.KEY_D,
        uinput.KEY_Z,
        uinput.KEY_X,
        uinput.KEY_C,
        uinput.KEY_UP,
        uinput.KEY_DOWN,
        uinput.KEY_LEFT,
        uinput.KEY_RIGHT,
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
            controller.emit(uinput.KEY_A, 1)
            controller.emit(uinput.KEY_A, 0)
        case "S":
            print("GB R")
            controller.emit(uinput.KEY_S, 1)
        case "D":
            print("GB START")
            controller.emit(uinput.KEY_D)controller.emit(uinput.KEY_X, 1)
        case "Z":
            print("GB A")
            controller.emit(uinput.KEY_Z, 1)
            controller.emit(uinput.KEY_Z, 0)
        case "X":
            print("GB B")
            controller.emit(uinput.KEY_X, 1)
            controller.emit(uinput.KEY_X, 0)
        case "C":
            print("GB SELECT")
            controller.emit(uinput.KEY_C)
        case "&":
            print("GB UP")
            controller.emit(uinput.KEY_UP)
        case "(":
            print("GB DOWN")
            controller.emit(uinput.KEY_DOWN)
        case "%":
            print("GB LEFT")
            controller.emit(uinput.KEY_LEFT)
        case "'":
            print("GB RIGHT")
            controller.emit(uinput.KEY_RIGHT)

        case _:
            pass

    return ""


if __name__ == '__main__':
    app.run()
