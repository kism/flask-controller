host = "127.0.0.1"
port = "5001"

sockettest = nil



function ST_stop()
	if not sockettest then return end
	console:log("Socket Test: Shutting down")
	sockettest:close()
	sockettest = nil
end

function ST_start()
	ST_stop()
	console:log("Socket Test: Connecting to " .. host .. ":" .. port)
	sockettest = socket.tcp()
	sockettest:add("received", ST_received)
	sockettest:add("error", ST_error)
	if sockettest:connect(host, port) then
		console:log("Socket Test: Connected")
	else
		console:log("Socket Test: Failed to connect")
		ST_stop()
	end
end

function ST_error(err)
	console:error("Socket Test Error: " .. err)
	ST_stop()
end

function ST_received()
	while true do
		local p, err = sockettest:receive(1024)
		if p then
			console:log("Socket Test Received: " .. p:match("^(.-)%s*$"))
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error("Socket Test Error: " .. err)
				ST_stop()
			end
			return
		end
	end
end

callbacks:add("start", ST_start)
callbacks:add("stop", ST_stop)
callbacks:add("crashed", ST_stop)
callbacks:add("reset", ST_start)

-- callbacks:add("frame", ST_start)
