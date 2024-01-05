--[[
Copyright (c) 2023 Zunawe
Copyright (c) 2023 KiSM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
]]

-- Bizhawk port of my mgba code, ty Zunawe for connector_bizhawk_generic.lua
-- Needs the archipelago lua socket libs (included)

-- Input Mapping Table
-- 10  ,9 ,8   ,7 ,6   ,5    ,4    ,3     ,2,1
-- 512,256,128 ,64,32  ,16   ,8    ,4     ,2,1
-- L  ,R  ,Down,Up,Left,Right,Start,Select,B,A

INPUTBUFFER = {}
LASTINPUT = {}

local bizhawk_version = client.getversion()
local bizhawk_major, bizhawk_minor, bizhawk_patch = bizhawk_version:match("(%d+)%.(%d+)%.?(%d*)")
bizhawk_major = tonumber(bizhawk_major)
bizhawk_minor = tonumber(bizhawk_minor)
if bizhawk_patch == "" then
    bizhawk_patch = 0
else
    bizhawk_patch = tonumber(bizhawk_patch)
end

local lua_major, lua_minor = _VERSION:match("Lua (%d+)%.(%d+)")
lua_major = tonumber(lua_major)
lua_minor = tonumber(lua_minor)

if lua_major > 5 or (lua_major == 5 and lua_minor >= 3) then
    require("lua_5_3_compat")
end

local socket = require("socket")

-- Set to log incoming requests
-- Might cause lag due to large console output
local DEBUG = true

local SOCKET_PORT = 5001

local STATE_NOT_CONNECTED = 0
local STATE_CONNECTED = 1

local server = nil
local client_socket = nil

local current_state = STATE_NOT_CONNECTED

local timeout_timer = 0
local message_timer = 0
local message_interval = 0
local prev_time = 0
local current_time = 0

local locked = false

local rom_hash = nil

function lock()
    locked = true
    client_socket:settimeout(2)
end

function unlock()
    locked = false
    client_socket:settimeout(0)
end

-- No idea why I can't just receive two bytes
function send_receive()
    -- Try receive a byte via the socket client
    local p1, err = client_socket:receive(1)
    if p1 then
        -- If we have a byte, convert the first part to an actual byte datatype
        p1 = string.byte(p1)

        -- Grab the second byte
        local p2, err = client_socket:receive(1)
        p2 = string.byte(p2)
        p2 = bit.lshift(p2, 8) -- Offset the second byte since it will be the upper of the two bytes

        -- Or the two bytes together, adding them works too, insert into INPUTBUFFER
        table.insert(INPUTBUFFER, bit.bor(p1, p2))
    end

    -- Handle errors
    if err == "closed" then
        if current_state == STATE_CONNECTED then
            print_everywhere("Connection to client closed")

        end
        current_state = STATE_NOT_CONNECTED
        return
    elseif err == "timeout" then
        unlock()
        return
    elseif err ~= nil then
        print("send_receive error: " .. err)
        current_state = STATE_NOT_CONNECTED
        unlock()
        return
    end

    -- Reset timeout timer
    timeout_timer = 5

end

function initialize_server()
    local err
    local port = SOCKET_PORT
    local res = nil

    server, err = socket.socket.tcp4()
    while res == nil do

        res, err = server:bind("localhost", port)
        if res == nil and err ~= "address already in use" then
            print(err)
            return
        end
    end

    res, err = server:listen(0)

    if err ~= nil then
        print(err)
        return
    end

    server:settimeout(0)
end

function print_everywhere(message)
    print(message)
    gui.addmessage(message)
end

function main()
    while true do
        if server == nil then
            initialize_server()
        end

        current_time = socket.socket.gettime()
        timeout_timer = timeout_timer - (current_time - prev_time)
        message_timer = message_timer - (current_time - prev_time)
        prev_time = current_time

        if current_state == STATE_NOT_CONNECTED then
            if emu.framecount() % 120 == 0 then
                print_everywhere("Looking for client, listening on: " .. SOCKET_PORT)
                local client, timeout = server:accept()
                if timeout == nil then
                    print_everywhere("Client connected")
                    current_state = STATE_CONNECTED
                    client_socket = client
                    server:close()
                    server = nil
                    client_socket:settimeout(0)
                end
            end
        else
            repeat
                send_receive()
            until not locked
        end

        coroutine.yield()
    end
end

function checkbit(byte1, mask)
    return (byte1 & mask) ~= 0
end

function SetTheKeys()
    if next(INPUTBUFFER) ~= nil then
        local numhopefully = table.remove(INPUTBUFFER)

        if DEBUG then
            print("Input: " .. numhopefully)
        end

        input = {}
        input['L'] = checkbit(numhopefully, 0x0200)
        input['R'] = checkbit(numhopefully, 0x0100)
        input['Down'] = checkbit(numhopefully, 0x0080)
        input['Up'] = checkbit(numhopefully, 0x0040)
        input['Left'] = checkbit(numhopefully, 0x0020)
        input['Right'] = checkbit(numhopefully, 0x0010)
        input['Start'] = checkbit(numhopefully, 0x0008)
        input['Select'] = checkbit(numhopefully, 0x0004)
        input['B'] = checkbit(numhopefully, 0x0002)
        input['A'] = checkbit(numhopefully, 0x0001)

        joypad.set(input)
        LASTINPUT = input
    else
        joypad.set(LASTINPUT)
    end
end

event.onexit(function()
    if server ~= nil then
        print("Closing server")
        server:close()
    end
    print("-- Ending Script --")
end)

print("\n-- Starting --")
print(_VERSION)
if bizhawk_major < 2 or (bizhawk_major == 2 and bizhawk_minor < 7) then
    print("Must use BizHawk 2.7.0 or newer")
elseif bizhawk_major > 2 or (bizhawk_major == 2 and bizhawk_minor > 9) then
    print("Warning: This version of BizHawk is newer than this script. If it doesn't work, consider downgrading to 2.9.")
else
    if emu.getsystemid() == "NULL" then
        print("No ROM is loaded. Please load a ROM.")
        while emu.getsystemid() == "NULL" do
            emu.frameadvance()
        end
    end

    rom_hash = gameinfo.getromhash()

    local emustatus = emu or false

    -- Print emulator info
    if emustatus then
        print("System running: " .. emu.getsystemid())
        print("Game hash: " .. rom_hash)
    else
        print("No Game Running!")
    end

    print("Waiting for client to connect.")

    local co = coroutine.create(main)
    function tick()
        local status, err = coroutine.resume(co)

        if not status and err ~= "cannot resume dead coroutine" then
            print("\nERROR: " .. err)
            print("Consider reporting this crash.\n")

            if server ~= nil then
                server:close()
            end

            co = coroutine.create(main)
        end
    end

    -- Gambatte has a setting which can cause script execution to become
    -- misaligned, so for GB and GBC we explicitly set the callback on
    -- vblank instead.
    -- https://github.com/TASEmulators/BizHawk/issues/3711
    if emu.getsystemid() == "GB" or emu.getsystemid() == "GBC" or emu.getsystemid() == "SGB" then
        event.onmemoryexecute(tick, 0x40, "tick", "System Bus")
    else
        event.onframeend(tick)
    end

    while true do
        SetTheKeys()
        emu.frameadvance()
    end
end
