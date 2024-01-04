-- Sockets related
socket = require("socket") --- https://github.com/alain-riedinger/luasocket/releases/tag/3.0-5.4.3
SERVER = nil
ST_SOCKETS = {}
NEXTID = 1
local port = 5001

-- Input Mapping Table
-- 10  ,9 ,8   ,7 ,6   ,5    ,4    ,3     ,2,1
-- 512,256,128 ,64,32  ,16   ,8    ,4     ,2,1
-- L  ,R  ,Down,Up,Left,Right,Start,Select,B,A

INPUTBUFFER = {}

console.log("")
console.log("-- Starting --")

function ST_stop(id)
    local sock = ST_SOCKETS[id]
    ST_SOCKETS[id] = nil
    sock.close()
end

function ST_format(id, msg, isError)
    msg = msg or ""
    local prefix = "Socket " .. id
    if isError then
        prefix = prefix .. " Error: "
    else
        prefix = prefix .. " Received: "
    end
    return prefix .. msg
end

function ST_error(id, err)
    console.error(ST_format(id, err, true))
    ST_stop(id)
end

function ST_received(id)
    local sock = ST_SOCKETS[id]
    if not sock then
        return
    end
    while true do
        local p, err = sock.receive(2)
        if p then
            -- Add input to input buffer
            table.insert(INPUTBUFFER, p)
        else
            if err ~= socket.ERRORS.AGAIN then
                console.error(ST_format(id, err, true))
                ST_stop(id)
            end
            return
        end
    end
end



-- This is the realest
function SetTheKeys()
    if next(INPUTBUFFER) ~= nil then
        local p = table.remove(INPUTBUFFER)
        local numhopefully = string.byte(p)
        console.log("Input: " .. numhopefully)
        emu.setKeys(numhopefully)
    end
end



-- Main
while not SERVER do
    console.log(_VERSION)
    local emustatus = emu or false

    if emustatus then
        console.log("System running: " .. emu.getsystemid())
    else
        console.log("No Game Running!")
    end

    local err
    SERVER, err = socket.bind("0.0.0.0", port)
    if err then
        if err == socket.ERRORS.ADDRESS_IN_USE then
            console.log("Address in use")
        else
            console.error(ST_format("Bind", err, true))
            break
        end
    else
        local ok
        ok, err = SERVER:accept()
        if err then
            SERVER.close()
            console.error(ST_format("Listen", err, true))
        else
            console.log("Socket SERVER: Listening on port " .. port)
            SERVER.add("received", ST_accept)
        end
    end
end


--- Real loop
while true do
    SetTheKeys()
    emu.frameadvance()
end