#!/usr/bin/env python2
from PyQt4 import QtGui
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
import sip, sys
from gnuradio import iio, qtgui
import argparse
from bitstring import BitArray
from gnuradio import uhd
from Queue import Queue


class top_block(gr.top_block):

    def __init__(self, args):
        gr.top_block.__init__(self, "Nordic Single-Channel Receiver Example")

        self.qapp = QtGui.QApplication(sys.argv)
        
        # SDR configuration
        self.freq = 2400e6 + args.channel * 1e6
        self.gain = args.gain
        self.symbol_rate = args.data_rate
        self.sample_rate = args.data_rate * args.samples_per_symbol
       

        dr = 0
        if args.data_rate == 1e6:
            dr = 1
        elif args.data_rate == 2e6:
            dr = 2

        # SDR sink (gr-osmosdr sink)
        #self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + '' )
        #self.osmosdr_sink_0.set_sample_rate(self.sample_rate * channel_count)
        #self.osmosdr_sink_0.set_center_freq(self.freq, 0)
        #self.osmosdr_sink_0.set_freq_corr(0, 0)
        #self.osmosdr_sink_0.set_gain(self.gain, 0)
        #self.osmosdr_sink_0.set_if_gain(20, 0)
        #self.osmosdr_sink_0.set_bb_gain(20, 0)
        #self.osmosdr_sink_0.set_antenna('TX/RX', 0)
        #self.osmosdr_sink_0.set_bandwidth(0, 0)
        #self.pluto_sink = iio.pluto_sink('192.168.2.1', int(self.freq), int(int(self.sample_rate)), int(2e6), 0x8000, False, 10.0, '', True)
        self.osmosdr_sink = osmosdr.sink()
        self.osmosdr_sink.set_sample_rate(self.sample_rate)
        self.osmosdr_sink.set_center_freq(self.freq)
        self.osmosdr_sink.set_gain(self.gain)
        self.osmosdr_sink.set_antenna('TX/RX')
        
        self.snk = qtgui.sink_c(
            1024, #fftsize
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            self.sample_rate, #bw
            "", #name
            True, #plotfreq
            False, #plotwaterfall
            True, #plottime
            False, #plotconst
        )

        # Low Pass filter
        self.lpf = filter.fir_filter_ccf(
            1, firdes.low_pass_2(1, self.sample_rate, self.symbol_rate / 2, 100e3, 50))

        # Modulators and packet framers
        self.nordictap_transmitter = nordic.nordictap_transmitter([args.channel])
        self.gfsk_mod = digital.gfsk_mod(
            samples_per_symbol=2,
        	sensitivity=0.78,
        	bt=0.5,
        	verbose=True,
        	log=True,
        	)
        self.tx = nordic.nordic_tx(1)
        
        #self.connect(self.nordictap_transmitter, self.tx)
        self.connect(self.tx, self.gfsk_mod)
        self.connect(self.gfsk_mod, self.lpf)
        self.connect(self.lpf, self.osmosdr_sink)
        #self.connect(self.lpf, self.snk)
        
        # Tell the sink we want it displayed
        self.pyobj = sip.wrapinstance(self.snk.pyqwidget(), QtGui.QWidget)
        self.pyobj.show()
        
        #self.blocks_message_debug = blocks.message_debug()

        # Wire up output packet connection
        self.msg_connect(self.nordictap_transmitter,
                         "nordictap_out", self.tx, "nordictap_in")
        #self.msg_connect(self.nordictap_transmitter,
              #           "nordictap_out", self.blocks_message_debug, "print")
			

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser('Nordic Single Channel Transmitter Example',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=120))
    
    parser.add_argument(
        '-c', '--channel', type=int, help='RF channel (0-125)', default=85)
    parser.add_argument('-r', '--data_rate', type=float,
                        help='Data Rate (250e3, 1e6 or 2e6', default=2e6, choices=[250e3, 1e6, 2e6])
    parser.add_argument('-l', '--crc_length', type=int,
                        help='CRC Length (1-2)', default=2, choices=[1, 2])
    parser.add_argument('-a', '--address_length', type=int,
                        help='Address Length (3-5)', default=5, choices=[3, 4, 5])
    parser.add_argument('-s', '--samples_per_symbol',
                        type=int, help='Samples Per Symbol', default=2)
    
    parser.add_argument(
        '-g', '--gain', type=float, help='Radio Gain', default=30)

    args = parser.parse_args()

    tb = top_block(args)
    tb.start()
    #tb.qapp.exec_()
    # Transmit some packets, hopping between three channels
    address = '\x55\x55\x55\x55\x55'
    payload = '\x20\x20\x20\x20\x32\x30\x2E\x32'
    sequence_number = 0
    while True:
		tb.nordictap_transmitter.transmit(
                address, payload, 0, sequence_number)
		time.sleep(0.5)
    
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
