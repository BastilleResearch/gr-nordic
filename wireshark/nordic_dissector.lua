-- trivial protocol example
-- declare our protocol
nordic_proto = Proto("nordic","Nordic Semiconductor nRF24L")
-- create a function to dissect it
function nordic_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "NORDIC"
    local subtree = tree:add(nordic_proto,buffer(),"nRF24L Packet")
    pinfo.cols.info = ""

    -- channel
    local channel = buffer(0,1):uint()

    -- data rate
    local data_rate = buffer(1,1):uint()
    local data_rate_string = ""
    if data_rate == 0 then data_rate_string = "250K" end
    if data_rate == 1 then data_rate_string = "1M" end
    if data_rate == 2 then data_rate_string = "2M" end

    -- address length
    local address_length = buffer(2,1):uint()

    -- payload length
    local payload_length = buffer(3,1):uint()

    -- sequence number
    local sequence_number = buffer(4,1):uint()

    -- no ack bit
    local no_ack = buffer(5,1):uint()

    -- crc length
    local crc_length = buffer(6,1):uint()

    -- dynamic payloads bit
    local dynamic_payload = buffer(7,1):uint()

    -- address
    local address = buffer(8,address_length)
    local address_bytes = address:bytes()

    -- payload
    local payload = buffer(8+address_length,payload_length)
    local payload_bytes = payload:bytes()

    -- crc
    local crc = buffer(8+address_length+payload_length, crc_length)

    subtree:add(buffer(0,1), "Channel:         " .. (2400+channel) .. "MHz")
    subtree:add(buffer(1,1), "Data Rate:       " .. data_rate_string)
    subtree:add(buffer(2,1), "Address Length:  " .. address_length)
    subtree:add(buffer(3,1), "Payload Length:  " .. payload_length)
    subtree:add(buffer(4,1), "Sequence Number: " .. sequence_number)
    subtree:add(buffer(5,1), "No ACK:          " .. no_ack)
    subtree:add(buffer(6,1), "Dynamic Payload: " .. dynamic_payload)
    subtree:add(buffer(7,1), "CRC Length:      " .. crc_length)
    subtree:add(buffer(8,address_length), "Address:         " .. address)
    subtree:add(buffer(8+address_length,payload_length), "Payload:         " .. payload)
    subtree:add(buffer(8+address_length+payload_length, crc_length), "CRC:             " .. crc)

    -- Keepalive (vendor agnostic)
    if payload_bytes:len() == 0 then
      pinfo.cols.info = "ACK"
    end

    -- Microsoft
    if bit.band(buffer(7,1):uint(), 0xF0) == 0xA0 and payload_length > 0 then 

      -- Validate the checksum (AES encrypted series)
      local sum = 0xFF
      for x = 0, payload_bytes:len()-1 do
        sum = bit.bxor(sum, payload_bytes:get_index(x))
      end
      sum = bit.band(sum, 0xFF)
      if sum == 0 then

        -- Microsoft keepalive
        if payload_bytes:get_index(1) == 0x38 and payload_bytes:len() == 8 then
          pinfo.cols.info = "Keepalive"
        end

        -- Microsoft mouse movement/click 
        if payload_bytes:get_index(1) == 0x90 then

          local vtree = subtree:add(nordic_proto, buffer(), "Microsoft Movement/Click")
          pinfo.cols.info = "Microsoft Mouse Movement/Click"
          vtree:add(string.format("Device Type: 0x%02x", payload_bytes:get_index(2)))

          -- Movement X/Y
          local movement_x = payload(9, 2):le_int()
          local movement_y = payload(11, 2):le_int()
          local scroll = payload(13, 2):le_int()
          vtree:add(string.format("Movement X:   %i", movement_x))
          vtree:add(string.format("Movement Y:   %i", movement_y))
          vtree:add(string.format("Scroll Wheel: %i", scroll))

          -- Button mask 
          local button_mask = payload(8, 1):uint()
          vtree:add(string.format("Button 0:     %i", bit.band(bit.rshift(button_mask, 0), 1)))
          vtree:add(string.format("Button 1:     %i", bit.band(bit.rshift(button_mask, 1), 1)))
          vtree:add(string.format("Button 2:     %i", bit.band(bit.rshift(button_mask, 2), 1)))
          vtree:add(string.format("Button 3:     %i", bit.band(bit.rshift(button_mask, 3), 1)))
          vtree:add(string.format("Button 4:     %i", bit.band(bit.rshift(button_mask, 4), 1)))
          vtree:add(string.format("Button 5:     %i", bit.band(bit.rshift(button_mask, 5), 1)))
          vtree:add(string.format("Button 6:     %i", bit.band(bit.rshift(button_mask, 6), 1)))
          vtree:add(string.format("Button 7:     %i", bit.band(bit.rshift(button_mask, 7), 1)))

        end

      end
    end

end

-- load the udp.port table
udp_table = DissectorTable.get("udp.port")

-- register our protocol to handle udp port 7777
udp_table:add(9451,nordic_proto)