document.onkeydown = function (e) {
    get = window.event ? event : e;
    key = get.keyCode ? get.keyCode : get.charCode;
    key = String.fromCharCode(key);

    validkey = false
    switch (key) {
        case "A":
            document.getElementById('GBA_KEY_L').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "S":
            document.getElementById('GBA_KEY_R').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "D":
            document.getElementById('GBA_KEY_START').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "Z":
            document.getElementById('GBA_KEY_B').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "X":
            document.getElementById('GBA_KEY_A').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "C":
            document.getElementById('GBA_KEY_SELECT').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "&":
            document.getElementById('GBA_KEY_UP').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "(":
            document.getElementById('GBA_KEY_DOWN').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "%":
            document.getElementById('GBA_KEY_LEFT').style.backgroundColor = '#003F87';
            validkey = true;
            break;
        case "'":
            document.getElementById('GBA_KEY_RIGHT').style.backgroundColor = '#003F87';
            validkey = true;
            break;
    }


    if (validkey == true) {
        fetch(`/ProcessUserInput/%22${key}%22`, {
            method: 'POST'
        })
            .then(response => {
                console.log('Sent:', key, '| Response code:', response.status);
                if (response.status == "200") {
                    document.getElementById('TITLE').style.color = '#CCFFCC';
                } else {
                    document.getElementById('TITLE').style.color = '#FFCCCC';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('TITLE').style.color = '#FFCCCC';
            });
    }
}

document.onkeyup = function (e) {
    get = window.event ? event : e;
    key = get.keyCode ? get.keyCode : get.charCode;
    key = String.fromCharCode(key);
    // console.log(key);

    validkey = false
    switch (key) {
        case "A":
            document.getElementById('GBA_KEY_L').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "S":
            document.getElementById('GBA_KEY_R').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "D":
            document.getElementById('GBA_KEY_START').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "Z":
            document.getElementById('GBA_KEY_B').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "X":
            document.getElementById('GBA_KEY_A').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "C":
            document.getElementById('GBA_KEY_SELECT').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "&":
            document.getElementById('GBA_KEY_UP').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "(":
            document.getElementById('GBA_KEY_DOWN').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "%":
            document.getElementById('GBA_KEY_LEFT').style.backgroundColor = '#222222';
            validkey = true;
            break;
        case "'":
            document.getElementById('GBA_KEY_RIGHT').style.backgroundColor = '#222222';
            validkey = true;
            break;
    }
}