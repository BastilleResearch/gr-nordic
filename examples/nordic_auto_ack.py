#!/usr/bin/env python2

from gnuradio import gr, blocks, digital, filter
from gnuradio.filter import firdes
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
        gr.top_block.__init__(self, "Nordic Auto-ACK Example")

        # SDR configuration
        self.freq = 2400e6 + args.channel * 1e6
        self.gain = args.gain
        self.symbol_rate = args.data_rate
        self.sample_rate = args.data_rate * args.samples_per_symbol

        # SDR source (gr-osmosdr source)
        self.osmosdr_source = osmosdr.source()
        self.osmosdr_source.set_sample_rate(self.sample_rate)
        self.osmosdr_source.set_center_freq(self.freq)
        self.osmosdr_source.set_gain(self.gain)
        self.osmosdr_source.set_antenna('TX/RX')

        # SDR sink (gr-osmosdr source)
        self.osmosdr_sink = osmosdr.sink()
        self.osmosdr_sink.set_sample_rate(self.sample_rate)
        self.osmosdr_sink.set_center_freq(self.freq)
        self.osmosdr_sink.set_gain(self.gain)
        self.osmosdr_sink.set_antenna('TX/RX')

        # Transmit chain
        self.tx = nordic.nordic_tx()
        self.gfsk_mod = digital.gfsk_mod(
            samples_per_symbol=args.samples_per_symbol)
        self.connect(self.tx, self.gfsk_mod)
        self.connect(self.gfsk_mod, self.osmosdr_sink)

        # Receive chain
        dr = 0
        if args.data_rate == 1e6:
            dr = 1
        elif args.data_rate == 2e6:
            dr = 2
        self.rx = nordic.nordic_rx(
            args.channel, args.address_length, args.crc_length, dr)
        self.gfsk_demod = digital.gfsk_demod(
            samples_per_symbol=args.samples_per_symbol)
        self.lpf = filter.fir_filter_ccf(
            1, firdes.low_pass_2(1, self.sample_rate, self.symbol_rate / 2, 50e3, 50))
        self.connect(self.osmosdr_source, self.lpf)
        self.connect(self.lpf, self.gfsk_demod)
        self.connect(self.gfsk_demod, self.rx)

        # Handle incoming packets
        self.nordictap_ack_handler = nordictap_ack_handler()
        self.msg_connect(self.rx, "nordictap_out",
                         self.nordictap_ack_handler, "nordictap_in")

        # Reply with ACKs
        self.msg_connect(self.nordictap_ack_handler,
                         "nordictap_out", self.tx, "nordictap_in")


# Nordic Auto-ACK handler
class nordictap_ack_handler(gr.sync_block):

    # Constructor

    def __init__(self):
        gr.sync_block.__init__(
            self, name="Nordictap Handler", in_sig=None, out_sig=None)

        # Received packet input port
        self.message_port_register_in(pmt.intern("nordictap_in"))
        self.set_msg_handler(
            pmt.intern("nordictap_in"), self.nordictap_handler)

        # ACK output port
        self.message_port_register_out(pmt.intern("nordictap_out"))

    # Handle incoming packets, and reply with ACKs
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

        # ACK if needed
        if payload_length > 0 and no_ack == 0:

            # Print the channel, sequence number, address and payload
            print "ACK'd Packet: ",
            print 'CH=' + str(2400 + channel),
            print 'SEQ=' + str(sequence_number),
            print 'ADDR=' + ':'.join('%02X' % ord(b) for b in address),
            print 'PLD=' + ':'.join('%02X' % ord(b) for b in payload),
            print 'CRC=' + ':'.join('%02X' % ord(b) for b in crc)

            # Build an ACK
            nordictap = [0] + [4, 2, 5, 0, sequence_number, 0, 2]
            for c in address:
                nordictap.append(ord(c))

            # Transmit an ACK
            vec = pmt.make_u8vector(len(nordictap), 0)
            for x in range(len(nordictap)):
                pmt.u8vector_set(vec, x, nordictap[x])
            self.message_port_pub(pmt.intern("nordictap_out"), vec)


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser('Nordic Auto-ACK Example',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=120))
    parser.add_argument(
        '-c', '--channel', type=int, help='RF channel (0-125)', default=4)
    parser.add_argument('-r', '--data_rate', type=float,
                        help='Data Rate (250e3, 1e6 or 2e6', default=2e6, choices=[250e3, 1e6, 2e6])
    parser.add_argument('-l', '--crc_length', type=int,
                        help='CRC Length (1-2)', default=2, choices=[1, 2])
    parser.add_argument('-a', '--address_length', type=int,
                        help='Address Length (3-5)', default=5, choices=[3, 4, 5])
    parser.add_argument('-s', '--samples_per_symbol',
                        type=int, help='Samples Per Symbol', default=2)
    parser.add_argument(
        '-g', '--gain', type=float, help='Radio Gain', default=80)

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
