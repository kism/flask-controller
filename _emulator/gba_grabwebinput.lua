-- Sockets related
SERVER = nil
ST_SOCKETS = {}
NEXTID = 1
local port = 5001

-- Input Mapping Table
-- 10  ,9 ,8   ,7 ,6   ,5    ,4    ,3     ,2,1
-- 512,256,128 ,64,32  ,16   ,8    ,4     ,2,1
-- L  ,R  ,Down,Up,Left,Right,Start,Select,B,A

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
        local p, err = sock:receive(2)
        if p then
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

-- This is the realest
function SetTheKeys()
    if next(INPUTBUFFER) ~= nil then
        local p = table.remove(INPUTBUFFER)
        console:log("On this frame")

        local numhopefully = string.byte(p)
        -- console:log("Type: " .. type(numhopefully))
        console:log("Value: " .. numhopefully)

        emu:setKeys(numhopefully)
    end
end

callbacks:add("frame", SetTheKeys) -- Runs activeHunt() every frame

-- Main
while not SERVER do
    -- local gamecode =
    -- if emu == not nil then
    --     console:log("Running game: " .. emu:getGameCode())
    -- else
    --     console:log("No Game Running!")
    -- end
    console:log(_VERSION)
    console:log("If the next line is an error, no game is loaded, I cant figure out the logic to detect this.")
    console:log("Running game: " .. emu:getGameCode())

    local err
    SERVER, err = socket.bind(nil, port)
    if err then
        if err == socket.ERRORS.ADDRESS_IN_USE then
            console:log("Address in use")
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
