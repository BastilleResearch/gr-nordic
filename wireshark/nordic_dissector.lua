-- trivial protocol example
-- declare our protocol
nordic_proto = Proto("nordic","Nordic Semiconductor nRF24L")
-- create a function to dissect it
function nordic_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "NORDIC"
    local subtree = tree:add(nordic_proto,buffer(),"nRF24L Packet")

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

    -- address
    local address = buffer(7,address_length)

    -- payload
    local payload = buffer(7+address_length,payload_length)

    -- crc
    local crc = buffer(7+address_length+payload_length, crc_length)

    subtree:add(buffer(0,1), "Channel:         " .. (2400+channel) .. "MHz")
    subtree:add(buffer(1,1), "Data Rate:       " .. data_rate_string)
    subtree:add(buffer(2,1), "Address Length:  " .. address_length)
    subtree:add(buffer(3,1), "Payload Length:  " .. payload_length)
    subtree:add(buffer(4,1), "Sequence Number: " .. sequence_number)
    subtree:add(buffer(5,1), "No ACK:          " .. no_ack)
    subtree:add(buffer(6,1), "CRC Length:      " .. crc_length)
    subtree:add(buffer(7,address_length), "Address:         " .. address)
    subtree:add(buffer(7+address_length,payload_length), "Payload:         " .. payload)
    subtree:add(buffer(7+address_length+payload_length, crc_length), "CRC:             " .. crc)

    -- Classify Microsoft packets
    if bit.band(buffer(7,1):uint(), 0xF0) == 0xA0 and payload_length > 0 then 

      payload_bytes = payload:bytes()
      
      -- Validate the checksum
      local sum = 0
      for x = 0, payload_bytes:len()-1 do
        sum = sum + payload_bytes:get_index(x)
      end
      sum = bit.band(sum, 0xFF)
      if sum == 0 or true then

        if bit.band(buffer(11,1):uint(), 0x0F) == 0x06 then
          subtree:add(buffer(11, 1), "Device Type:     Microsoft Mouse")
        else
          subtree:add(buffer(11, 1), "Device Type:     Microsoft (Unknown)")
        end
      end
    end

end

-- load the udp.port table
udp_table = DissectorTable.get("udp.port")

-- register our protocol to handle udp port 7777
udp_table:add(9451,nordic_proto)