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

function getdakeys()
    local keys = emu:getKeys()
    console:log(tostring(emu:getKeys()))
end

callbacks:add("frame", getdakeys) -- Runs activeHunt() every frame
