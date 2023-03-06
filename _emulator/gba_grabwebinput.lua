-- Sockets related
SERVER     = nil
ST_SOCKETS = {}
NEXTID     = 1
local port = 5001


-- Input Related
FRAMEDELAY = 0

function ST_stop(id)
	local sock = ST_SOCKETS[id]
	ST_SOCKETS[id] = nil
	sock:close()
end

function ST_format(id, msg, isError)
	local prefix = "Socket " .. id
	if isError then
		prefix = prefix .. " Error: "
	else
		prefix = prefix .. " Received: "
	end
	return prefix .. msg
end

function ST_error(id, err)
	console:error(ST_format(id, err, true))
	ST_stop(id)
end

function ST_received(id)
	local sock = ST_SOCKETS[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			console:log(ST_format(id, p:match("^(.-)%s*$")))
			-- console.log(string(tonumber(p)))
			-- emu:setKey(tonumber(p))
			-- emu:setKey(1 << int(p))
			FRAMEDELAY = 3
			if p == "GBA_KEY_A" then
				emu:addKey(0)
			elseif p == "GBA_KEY_B" then
				emu:addKey(1)
			elseif p == "GBA_KEY_L" then
				emu:addKey(9)
			elseif p == "GBA_KEY_R" then
				emu:addKey(8)
			elseif p == "GBA_KEY_START" then
				emu:addKey(3)
			elseif p == "GBA_KEY_SELECT" then
				emu:addKey(2)
			elseif p == "GBA_KEY_UP" then
				emu:addKey(6)
			elseif p == "GBA_KEY_DOWN" then
				emu:addKey(7)
			elseif p == "GBA_KEY_LEFT" then
				emu:addKey(5)
			elseif p == "GBA_KEY_RIGHT" then
				emu:addKey(4)
			end
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error(ST_format(id, err, true))
				ST_stop(id)
			end
			return
		end
	end
end

function ST_accept()
	local sock, err = SERVER:accept()
	if err then
		console:error(ST_format("Accept", err, true))
		return
	end
	local id = NEXTID
	NEXTID = id + 1
	ST_SOCKETS[id] = sock
	sock:add("received", function() ST_received(id) end)
	sock:add("error", function() ST_error(id) end)
	console:log(ST_format(id, "Connected"))
end

function ResetKeys()
	if FRAMEDELAY > 0 then
		FRAMEDELAY = FRAMEDELAY - 1
	else
		emu:setKeys(0)
	end
end

callbacks:add("frame", ResetKeys) -- Runs activeHunt() every frame

-- Main
while not SERVER do
	local err
	SERVER, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			console.log("Address in use")
		else
			console:error(ST_format("Bind", err, true))
			break
		end
	else
		local ok
		ok, err = SERVER:listen()
		if err then
			SERVER:close()
			console:error(ST_format("Listen", err, true))
		else
			console:log("Socket SERVER Test: Listening on port " .. port)
			SERVER:add("received", ST_accept)
		end
	end
end
