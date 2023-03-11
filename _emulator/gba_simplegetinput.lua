function string.fromhex(str)
    return (str:gsub('..', function (cc)
        return string.char(tonumber(cc, 16))
    end))
end

function string.tohex(str)
    return (str:gsub('.', function (c)
        return string.format('%02X', string.byte(c))
    end))
end

function GetDaKeys()
    local keys = emu:getKeys()
    console:log(type(keys))
    console:log(tostring(keys))
end

callbacks:add("frame", GetDaKeys) -- Runs activeHunt() every frame


