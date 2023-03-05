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
        uinput.KEY_ENTER,
        uinput.KEY_BACKSLASH,
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
            pass

    return ""


if __name__ == '__main__':
    app.run()
