-- Imports
local lua_major, lua_minor = _VERSION:match("Lua (%d+)%.(%d+)")
lua_major = tonumber(lua_major)
lua_minor = tonumber(lua_minor)

if lua_major > 5 or (lua_major == 5 and lua_minor >= 3) then
    require("lua_5_3_compat")
end

local socket = require("socket")

-- Sockets related
server = nil
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
while not server do
    local err

    console.log(_VERSION)
    local emustatus = emu or false

    -- Print emulator info
    if emustatus then
        console.log("System running: " .. emu.getsystemid())
        rom_hash = gameinfo.getromhash()
        console.log("Game hash: " .. rom_hash)
    else
        console.log("No Game Running!")
    end

    -- Start socket server
    server, err = socket.socket.tcp4()
    if err then
        console.log("Could not create server: " .. err)
    end
    res, err = server:bind("localhost", port)
    if res == nil and err ~= "address already in use" then
        console.log("Address already in use: " .. err)
        return
    end

end

--- Real loop
while true do
    SetTheKeys()
    emu.frameadvance()
end
