// keyboard button:["GBA_KEY_NAME",<caurrently pressed>]
var inputdict = {
    65: ["GBA_KEY_L", false],
    83: ["GBA_KEY_R", false],
    68: ["GBA_KEY_START", false],
    90: ["GBA_KEY_B", false],
    88: ["GBA_KEY_A", false],
    67: ["GBA_KEY_SELECT", false],
    38: ["GBA_KEY_UP", false],
    40: ["GBA_KEY_DOWN", false],
    37: ["GBA_KEY_LEFT", false],
    39: ["GBA_KEY_RIGHT", false],
};

function postkey(key, updown) {
    var key = updown + inputdict[key][0];

    fetch(`/ProcessUserInput/${key}`, {
        method: "POST",
    })
        .then((response) => {
            console.log("Sent:", key, "| Response code:", response.status);
            if (response.status == "200") {
                document.getElementById("TITLE").style.color = "#CCFFCC";
            } else {
                document.getElementById("TITLE").style.color = "#FFCCCC";
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            document.getElementById("TITLE").style.color = "#FFCCCC";
        });
}

// Get Keypress
function getkey() {
    var get = window.event ? event : e;
    var key = get.keyCode ? get.keyCode : get.charCode;
    return key;
}

document.onkeydown = function (e) {
    var key = getkey();

    if (key in inputdict && inputdict[key][1] != true) {
        // If key is still currently held down, don't bother sending a duplicate POST due to windows keyboard character repeating
        document.getElementById(inputdict[key][0]).style.backgroundColor = "#003F87";
        inputdict[key][1] = true; // Mark button as being pressed down
        postkey(key, "D_");
    } else {
        console.log("Ignoring duplicate or invalid input");
    }
};

document.onkeyup = function (e) {
    var key = getkey();

    if (key in inputdict) {
        document.getElementById(inputdict[key][0]).style.backgroundColor = "#222222";
        inputdict[key][1] = false; // Mark button as being pressed down
        postkey(key, "U_");
    }
};
