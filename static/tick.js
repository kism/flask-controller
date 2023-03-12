function makeid () {
  var length = 15
  var result = ''
  const characters =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let counter = 0
  while (counter < length) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
    counter += 1
  }
  return result
}

console.log(makeid(5))

function getUpdate () {
  fetch('GetStatus', {
    method: 'GET',
    headers: {
      'client-id': clientid
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      return response.json()
    })
    .then(data => {
      // Do something with the data
      // console.log(data)
      if (data.sockconnected) {
        document.getElementById('FLASK_MGBA_STATS').innerHTML = `Connected`
        document.getElementById('FLASK_MGBA_STATS').style.color = '#CCFFCC'
      } else {
        document.getElementById('FLASK_MGBA_STATS').innerHTML = `Disconnected`
        document.getElementById('FLASK_MGBA_STATS').style.color = '#FFCCCC'
      }
      document.getElementById(
        'PLAYER_COUNT'
      ).innerHTML = `${data.playersconnected}`
    })
    .catch(error => {
      console.error('Could not GetStatus from webserver: ', error)
      document.getElementById('PLAYER_COUNT').innerHTML = `???`
      document.getElementById('FLASK_MGBA_STATS').innerHTML = `???`
      document.getElementById('FLASK_MGBA_STATS').style.color = '#FFCCCC'
      document.getElementById('HTTP_LATENCY').style.color = '#FFCCCC'
      document.getElementById('HTTP_LATENCY').innerHTML =
        'Cannot reach webserver'
    })
}

const clientid = makeid()
setInterval(getUpdate, 5000)
getUpdate()
