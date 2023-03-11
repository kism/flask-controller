function getUpdate () {
  fetch('GetStatus')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      return response.json()
    })
    .then(data => {
      // Do something with the data
      console.log(data)
      if (data.sockconnected) {
        document.getElementById('PLAYER_COUNT').innerHTML = `${data.playersconnected}`
        document.getElementById('FLASK_MGBA_STATS').innerHTML = `Connected`
        document.getElementById('FLASK_MGBA_STATS').style.color = '#CCFFCC'

      } else {
        document.getElementById('FLASK_MGBA_STATS').innerHTML = `Disconnected`
        document.getElementById('FLASK_MGBA_STATS').style.color = '#FFCCCC'
      }
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error)
      document.getElementById('FLASK_MGBA_STATS').innerHTML = `???`
      document.getElementById('FLASK_MGBA_STATS').style.color = '#FFCCCC'
    })

}

setInterval(getUpdate, 5000)
getUpdate()
