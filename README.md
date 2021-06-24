# gr-nordic

GNU Radio module and Wireshark dissector for the Nordic Semiconductor nRF24L Enhanced Shockburst protocol. 

## external c++ classes

### nordic_rx

Receiver class which consumes a GFSK demodulated bitstream and reconstructs Enhanced Shockburst packets. PDUs are printed standard out and sent to Wireshark.

### nordic_tx

Transmitter class which consumes nordictap structs, generates Enhanced Shockburst packets, and produces a byte stream to be fed to a GFSK modulator. 

## python examples

All python examples use the osmosdr_source/osmosdr_sink blocks, and are SDR agnostic. 

### nordic_receiver.py

Single channel receiver. Listening on channel 4 (2404MHz) with a 2Mbps data rate, 5 byte address, and 2 byte CRC is invoked as follows: 

```./nordic_receiver.py --channel 4 --data_rate 2e6 --crc_length 2 --address_length 5 --samples_per_symbol 2 --gain 40```

### nordic_auto_ack.py

Single channel receiver with auto-ACK. Listening (and ACKing) on channel 4 (2404MHz) with a 2Mbps data rate, 5 byte address, and 2 byte CRC is invoked as follows: 

```./nordic_auto_ack.py --channel 4 --data_rate 2e6 --crc_length 2 --address_length 5 --samples_per_symbol 2 --gain 40```

### nordic_sniffer_scanner.py

Sweeping single channel receiver, which sweeps between channels 2-83 looking for Enhanced Shockburst packets. During receive activity, it camps on a given channel until idle. 

```./nordic_sniffer_scanner.py ```

### microsoft_mouse_sniffer.py

Microsoft mouse/keyboard following receiver. When launched, this script will sweep between the 24 possible Microsoft wireless keyboard/mouse channels. When a device is found, it switches to that device's 4-channel group, sweeping between that set to follow the device. 

```./microsoft_mouse_sniffer.py ```

### nordic_channelized_receiver.py

Channelized receiver example, which tunes to 2414MHz, and receives 2Mbps Enhanced Shockburst packets on channels 10, 14, and 18. 

```./nordic_channelized_receiver.py ```

### nordic_channelized_transmitter.py

Channelized transmitter example, which tunes to 2414MHz, and transmits 2Mbps Enhanced Shockburst packets on channels 10, 14, and 18. 

```./nordic_channelized_transmitter.py ```

## wireshark dissector

The wireshark dissector will display Enhanced Shockburst packets in Wireshark. The logic is very straightforward, and will be simple to extend to classify various device types. 

### wireshark/nordic_dissector.lua

```wireshark -X lua_script:wireshark/nordic_dissector.lua -i lo -k -f udp ```

## nRF24LU1+ research firmware

Corresponding research firmware for the nRF24LU1+ chips (including Logitech Unifying dongles) is available [here](https://github.com/BastilleResearch/nrf-research-firmware/). 

Documentation on the packet formats covered by the MouseJack and KeySniffer vulnerability sets is available [here](https://github.com/BastilleResearch/mousejack/tree/master/doc/pdf). 
