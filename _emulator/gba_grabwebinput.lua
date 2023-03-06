lastkeys = nil
server = nil
ST_sockets = {}
nextID = 1

framedelay = 0

local KEY_NAMES = { "A", "B", "s", "S", "<", ">", "^", "v", "R", "L" }

function ST_stop(id)
	local sock = ST_sockets[id]
	ST_sockets[id] = nil
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
	local sock = ST_sockets[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			console:log(ST_format(id, p:match("^(.-)%s*$")))
			-- console.log(string(tonumber(p)))
			-- emu:setKey(tonumber(p))
			-- emu:setKey(1 << int(p))
			framedelay = 3
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

function ST_scankeys()
	local keys = emu:getKeys()
	if keys ~= lastkeys then
		lastkeys = keys
		local msg = "["
		for i, k in ipairs(KEY_NAMES) do
			if (keys & (1 << (i - 1))) == 0 then
				msg = msg .. " "
			else
				msg = msg .. k;
			end
		end
		msg = msg .. "]\n"
		for id, sock in pairs(ST_sockets) do
			if sock then sock:send(msg) end
		end
	end
end

function ST_accept()
	local sock, err = server:accept()
	if err then
		console:error(ST_format("Accept", err, true))
		return
	end
	local id = nextID
	nextID = id + 1
	ST_sockets[id] = sock
	sock:add("received", function() ST_received(id) end)
	sock:add("error", function() ST_error(id) end)
	console:log(ST_format(id, "Connected"))
end


function resetKeys()
	if framedelay > 0 then
		framedelay = framedelay -1
	else
		emu:setKeys(0)
	end
end

callbacks:add("keysRead", ST_scankeys)
callbacks:add("frame", resetKeys) -- Runs activeHunt() every frame

-- Main
local port = 5001
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			port = port + 1
		else
			console:error(ST_format("Bind", err, true))
			break
		end
	else
		local ok
		ok, err = server:listen()
		if err then
			server:close()
			console:error(ST_format("Listen", err, true))
		else
			console:log("Socket Server Test: Listening on port " .. port)
			server:add("received", ST_accept)
		end
	end
end
