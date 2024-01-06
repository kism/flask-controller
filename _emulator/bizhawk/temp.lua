-- This could use better math lmao
function send_receive()
    local p1, err = client_socket:receive(1)
    if p1 then
        p1 = string.byte(p1)

        local p2, err = client_socket:receive(1)
        p2 = string.byte(p2)
        p2 = bit.lshift(p2, 8)

        local p = bit.bor(p1, p2)

        table.insert(INPUTBUFFER, p)
    end
end