-- Sockets related
SERVER = nil
ST_SOCKETS = {}
NEXTID = 1
local port = 5001

-- Input Mapping Table
INPUTTAB = {}
INPUTTAB["GBA_KEY_A_____"] = 0
INPUTTAB["GBA_KEY_B_____"] = 1
INPUTTAB["GBA_KEY_L_____"] = 9
INPUTTAB["GBA_KEY_R_____"] = 8
INPUTTAB["GBA_KEY_START_"] = 3
INPUTTAB["GBA_KEY_SELECT"] = 2
INPUTTAB["GBA_KEY_UP____"] = 6
INPUTTAB["GBA_KEY_DOWN__"] = 7
INPUTTAB["GBA_KEY_LEFT__"] = 5
INPUTTAB["GBA_KEY_RIGHT_"] = 4

INPUTBUFFER = {}

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
    if not sock then
        return
    end
    while true do
        local p, err = sock:receive(16)
        if p then
            console:log(ST_format(id, p:match("^(.-)%s*$")))

            -- Add input to input buffer
            table.insert(INPUTBUFFER, p)
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
    sock:add("received", function()
        ST_received(id)
    end)
    sock:add("error", function()
        ST_error(id)
    end)
    console:log(ST_format(id, "Connected"))
end

function SetKeys()
    -- TODO USE THIS INSTEAD LMAO TODO
    -- 10  ,9 ,8   ,7 ,6   ,5    ,4    ,3     ,2,1
    -- 512,256,128 ,64,32  ,16   ,8    ,4     ,2,1
    -- L  ,R  ,Down,Up,Left,Right,Start,Select,B,A

    -- console:log(string(#INPUTBUFFER))
    local p = table.remove(INPUTBUFFER)

    console:log(p)

    local firstTwoChars = string.sub(p, 1, 2)
    local restOfString = string.sub(p, 3)

    if firstTwoChars == "D_" then
        console:log("Button Press")
        emu:addKey(INPUTTAB[restOfString])
    elseif firstTwoChars == "U_" then
        console:log("Button Release")
        emu:clearKey(INPUTTAB[restOfString])
    else
        console:log("Invalid input from socket")
    end
end

callbacks:add("frame", SetKeys) -- Runs activeHunt() every frame

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
            console:log("Socket SERVER: Listening on port " .. port)
            SERVER:add("received", ST_accept)
        end
    end
end
