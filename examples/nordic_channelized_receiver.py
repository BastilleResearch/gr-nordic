#!/usr/bin/env python2

from gnuradio import gr, blocks, digital, filter
from gnuradio.filter import firdes
from gnuradio import iio
import thread
import nordic
import pmt
import struct
import time
import numpy
import array
import osmosdr
import argparse
from bitstring import BitArray
from gnuradio import uhd
from Queue import Queue


class top_block(gr.top_block):

    def __init__(self, args):
        gr.top_block.__init__(self, "Nordic Single-Channel Receiver Example")

        self.freq = 2414e6
        self.gain = args.gain
        self.symbol_rate = 2e6
        self.sample_rate = 4e6

        # Channel map
        channel_count = 3
        channel_map = [14, 18, 10]

        # Data rate index
        dr = 2  # 2M

        # SDR source (gr-osmosdr source)
        #self.osmosdr_source = osmosdr.source()
        #self.osmosdr_source.set_sample_rate(self.sample_rate * channel_count)
        #self.osmosdr_source.set_center_freq(self.freq)
        #self.osmosdr_source.set_gain(self.gain)
        #self.osmosdr_source.set_antenna('TX/RX')
        self.pluto_source = iio.pluto_source('', int(self.freq), int(int(self.sample_rate * channel_count)), int(2e6), 0x8000, True, True, True, "manual", 64.0, '', True)
        #self.pluto_sink = iio.pluto_sink('192.168.2.1', int(self.freq), int(int(self.sample_rate * channel_count)), int(2e6), 0x8000, False, 10.0, '', True)

        # PFB channelizer
        taps = firdes.low_pass_2(
            1, self.sample_rate, self.symbol_rate / 2, 100e3, 30)
        self.channelizer = filter.pfb_channelizer_ccf(channel_count, taps, 1)

        # Stream to streams (PFB channelizer input)
        self.s2ss = blocks.stream_to_streams(
            gr.sizeof_gr_complex, channel_count)
        self.connect(self.pluto_source, self.s2ss)

        # Demodulators and packet deframers
        self.nordictap_printer = nordictap_printer()
        self.demods = []
        self.rxs = []
        for x in range(channel_count):
            self.connect((self.s2ss, x), (self.channelizer, x))
            self.demods.append(digital.gfsk_demod())
            self.rxs.append(nordic.nordic_rx(x, 5, 2, dr))
            self.connect((self.channelizer, x), self.demods[x])
            self.connect(self.demods[x], self.rxs[x])
            self.msg_connect(
                self.rxs[x], "nordictap_out", self.nordictap_printer, "nordictap_in")


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

        # Parse the address, payload, and crc
        address = data[7:7 + address_length]
        payload = data[7 + address_length:7 + address_length + payload_length]
        crc = data[7 + address_length + payload_length:
                   7 + address_length + payload_length + crc_length]

        # Print the channel, sequence number, address and payload
        print 'CH=' + str(2400 + channel),
        print 'SEQ=' + str(sequence_number),
        print 'ADDR=' + ':'.join('%02X' % ord(b) for b in address),
        print 'PLD=' + ':'.join('%02X' % ord(b) for b in payload),
        print 'CRC=' + ':'.join('%02X' % ord(b) for b in crc)


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser('Nordic Channelized Receiver Example',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=120))
    parser.add_argument(
        '-g', '--gain', type=float, help='Radio Gain', default=30)

    args = parser.parse_args()

    tb = top_block(args)
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
