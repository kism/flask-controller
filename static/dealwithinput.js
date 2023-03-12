/* eslint-disable no-irregular-whitespace */
// keyboard button:["GBA_KEY_NAME",<caurrently pressed>]
var inputdict = {
  65: ['GBA_KEY_L', false],
  83: ['GBA_KEY_R', false],
  68: ['GBA_KEY_START', false],
  90: ['GBA_KEY_B', false],
  88: ['GBA_KEY_A', false],
  67: ['GBA_KEY_SELECT', false],
  38: ['GBA_KEY_UP', false],
  40: ['GBA_KEY_DOWN', false],
  37: ['GBA_KEY_LEFT', false],
  39: ['GBA_KEY_RIGHT', false]
}

function postkey (key, updown) {
  var t0
  var t1
  var frames

  key = updown + inputdict[key][0]

  t0 = performance.now()

  fetch(`/ProcessUserInput/${key}`, {
    method: 'POST'
  })
    .then(response => {
      console.log('Sent:', key, '| Response code:', response.status)
      if (response.status == '200') {
        t1 = performance.now()
        frames = ((t1 - t0) * (1 / 60)).toFixed()

        if (frames < 1) {
          document.getElementById('HTTP_LATENCY').innerHTML = `＜1 frame`
          document.getElementById('HTTP_LATENCY').style.color = '#CCFFCC'
        } else if (frames == 1) {
          document.getElementById('HTTP_LATENCY').innerHTML = `　${frames} frame`
          document.getElementById('HTTP_LATENCY').style.color = '#CCFFCC'
        } else if (frames < 4) {
          document.getElementById('HTTP_LATENCY').innerHTML = `　${frames} frames`
          document.getElementById('HTTP_LATENCY').style.color = '#CCFFCC'
        } else {
          document.getElementById('HTTP_LATENCY').innerHTML = `　${frames} frames`
          document.getElementById('HTTP_LATENCY').style.color = '#FFCCCC'
        }
      } else {
        document.getElementById('HTTP_LATENCY').style.color = '#FFCCCC'
        document.getElementById('HTTP_LATENCY').innerHTML =
        'Something is wrong'
      }
    })
    .catch(error => {
      console.error('Could not ProcessUserInput to webserver: ', error)
      document.getElementById('HTTP_LATENCY').style.color = '#FFCCCC'
      document.getElementById('HTTP_LATENCY').innerHTML =
        'Cannot reach webserver'
      document.getElementById('FLASK_MGBA_STATS').innerHTML = `???`
      document.getElementById('FLASK_MGBA_STATS').style.color = '#FFCCCC'
    })
}

// Get Keypress
function getkey (e) {
  var get = window.event ? event : e
  var key = get.keyCode ? get.keyCode : get.charCode
  return key
}

document.onkeydown = function (e) {
  var key = getkey(e)

  if (key in inputdict && inputdict[key][1] != true) {
    // If key is still currently held down, don't bother sending a duplicate POST due to windows keyboard character repeating
    postkey(key, 'D_')
    document.getElementById(inputdict[key][0]).style.backgroundColor = '#003F87'
    inputdict[key][1] = true // Mark button as being pressed down
  } else {
    console.log('Ignoring duplicate or invalid input')
  }
}

document.onkeyup = function (e) {
  var key = getkey(e)

  if (key in inputdict) {
    postkey(key, 'U_')
    document.getElementById(inputdict[key][0]).style.backgroundColor = '#222222'
    inputdict[key][1] = false // Mark button as being pressed down
  }
}
