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
import random
import osmosdr
from gnuradio import iio
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

        # SDR sink (gr-osmosdr sink)
        self.osmosdr_sink = osmosdr.sink()
        self.osmosdr_sink.set_sample_rate(self.sample_rate * channel_count)
        self.osmosdr_sink.set_center_freq(self.freq)
        self.osmosdr_sink.set_gain(self.gain)
        self.osmosdr_sink.set_antenna('TX/RX')
        #self.pluto_sink = iio.pluto_sink('192.168.2.1', int(self.freq), int(int(self.sample_rate * channel_count)), int(2e6), 0x8000, False, 10.0, '', True)

        # PFB channelizer
        taps = firdes.low_pass_2(
            1, self.sample_rate, self.symbol_rate / 2, 100e3, 30)
        self.synthesizer = filter.pfb_synthesizer_ccf(channel_count, taps)

        # Modulators and packet framers
        self.nordictap_transmitter = nordic.nordictap_transmitter(channel_map)
        self.mods = []
        self.tx = nordic.nordic_tx(channel_count)
        for x in range(channel_count):
            self.mods.append(digital.gfsk_mod(
                samples_per_symbol=2,
        	    sensitivity=1.0,
        	    bt=0.35,
        	    verbose=True,
        	    log=True,))
            self.connect((self.tx, x), self.mods[x])
            self.connect(self.mods[x], (self.synthesizer, x))
        self.connect(self.synthesizer, self.osmosdr_sink)

        self.blocks_message_debug = blocks.message_debug()

        # Wire up output packet connection   
        self.msg_connect(self.nordictap_transmitter,
                         "nordictap_out", self.tx, "nordictap_in")
        self.msg_connect(self.nordictap_transmitter,
                         "nordictap_out", self.blocks_message_debug, "print")


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser('Nordic Channelized Transmitter Example',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=120))
    parser.add_argument(
        '-g', '--gain', type=float, help='Radio Gain', default=30)

    args = parser.parse_args()

    tb = top_block(args)
    tb.start()

    # Transmit some packets, hopping between three channels
    address = '\x55\x55\x55\x55\x55'
    payload = '\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA'
    sequence_number = 0
    while True:
        for x in range(3):
            tb.nordictap_transmitter.transmit(
                address, payload, x, sequence_number)
            sequence_number += 1
            if sequence_number > 3:
                sequence_number = 0
            time.sleep(0.2)

    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
