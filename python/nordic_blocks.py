#!/usr/bin/env python

from gnuradio import gr, blocks, digital
import _thread
import nordic
import pmt
import struct
import time
import numpy
import array
import random
import argparse
from bitstring import BitArray
from gnuradio import uhd
from queue import Queue

# Nordic transmitter strobe
class nordictap_transmitter(gr.sync_block):

    # Constructor

    def __init__(self, channel_map, address, payload, channel_index, sequence_number, big_packet):
        gr.sync_block.__init__(
            self, name="Nordictap Transmitter", in_sig=None, out_sig=None)

        self.channel_map = [channel_map]
        self.address = address
        self.payload = payload
        self.channel_index = channel_index
        self.sequence_number = sequence_number
        self.big_packet = big_packet
        
        # Packet output port
        self.message_port_register_in(pmt.intern("trig"))
        self.message_port_register_out(pmt.intern("nordictap_out"))
        
        self.set_msg_handler(pmt.intern("trig"), self.transmit)

    # Transmit a packet
    def transmit(self, msg):
		
        channel = self.channel_map[self.channel_index]
        
        if self.sequence_number == 4:
        	self.sequence_number = 0
        	
        #print address
        #print('SEQ=' + str(self.sequence_number))
        # Build a payload
        nordictap = [self.channel_index] + [
            channel, 2, len(self.address), len(self.payload), self.sequence_number, 0, 2, self.big_packet]
        for c in self.address:
            nordictap.append(ord(c))
        for c in self.payload:
            nordictap.append(ord(c))
        #print nordictap
        self.sequence_number += 1
        # Transmit packet
        #vec = pmt.make_u8vector(len(nordictap), 0)
        vec = pmt.init_u8vector(len(nordictap), nordictap)
        #for x in range(len(nordictap)):
         #   pmt.u8vector_set(vec, x, nordictap[x])
        self.message_port_pub(pmt.intern("nordictap_out"), vec)
        #time.sleep(0.2)
        
 # Nordic Printer
class nordictap_printer(gr.sync_block):

    # Constructor

    def __init__(self):
        gr.sync_block.__init__(
            self, name="Nordictap Printer", in_sig=None, out_sig=None)

        # Received packet input port
        self.message_port_register_in(pmt.intern("nordictap_in"))
        self.set_msg_handler(
            pmt.intern("nordictap_in"), self.nordictap_handler)

    # Handle incoming packets, and print payloads
    def nordictap_handler(self, msg):

        # PMT to byte string
        data = pmt.to_python(msg).tostring()

        # Unpack the header
        values = struct.unpack('BBBBBBBB', data[0:8])
        channel = values[0]
        data_rate = values[1]
        address_length = values[2]
        payload_length = values[3]
        sequence_number = values[4]
        no_ack = values[5]
        crc_length = values[6]
        big_packet = values[7]

        # Parse the address, payload, and crc
        address = data[8:8 + address_length]
        payload = data[8 + address_length:8 + address_length + payload_length]
        crc = data[8 + address_length + payload_length:
                   8 + address_length + payload_length + crc_length]

        # Print the channel, sequence number, address and payload
        print('CH=' + str(2400 + channel)),
        print('SEQ=' + str(sequence_number)),
        print('ADDR=' + ':'.join('%02X' % b for b in address)),
        print('PLD=' + ':'.join('%02X' % b for b in payload)),
        print('CRC=' + ':'.join('%02X' % b for b in crc))
        print('BP=' + str(big_packet))
