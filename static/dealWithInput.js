document.onkeydown = function(e) {
	get = window.event?event:e;
	key = get.keyCode?get.keyCode:get.charCode;
	key = String.fromCharCode(key);
	console.log(key);

    // POST YOURSELF
    const request = new XMLHttpRequest()
    request.open('POST', `/ProcessUserInput/${JSON.stringify(key)}`)
    request.send();
}