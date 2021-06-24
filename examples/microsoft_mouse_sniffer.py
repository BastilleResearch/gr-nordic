#!/usr/bin/env python2

from gnuradio import gr, blocks, digital, filter
from gnuradio.filter import firdes
import thread
import osmosdr
import nordic
import pmt
import struct
import time


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Microsoft Mouse Sniffer")

        # SDR configuration
        self.freq = 2403e6
        self.gain = 70
        self.symbol_rate = 2e6
        self.sample_rate = 4e6

        # SDR source (gr-osmosdr source)
        self.osmosdr_source = osmosdr.source()
        self.osmosdr_source.set_sample_rate(self.sample_rate)
        self.osmosdr_source.set_center_freq(self.freq)
        self.osmosdr_source.set_gain(self.gain)
        self.osmosdr_source.set_antenna('TX/RX')

        # Low pass filter
        self.lpf = filter.fir_filter_ccf(
            1, firdes.low_pass_2(1, self.sample_rate, self.symbol_rate / 2, 50e3, 50))

        # GFSK demod, defaults to 2 samples per symbol
        self.gfsk_demod = digital.gfsk_demod()

        # Nordic RX
        self.nordic_rx = nordic.nordic_rx(3, 5, 2, 2)

        # Connect the blocks
        self.connect((self.osmosdr_source, 0), (self.lpf, 0))
        self.connect((self.lpf, 0), (self.gfsk_demod, 0))
        self.connect((self.gfsk_demod, 0), (self.nordic_rx, 0))

        # Handle incoming packets
        self.nordictap_handler = microsoft_nordictap_handler(self)
        self.msg_connect(
            self.nordic_rx, "nordictap_out", self.nordictap_handler, "nordictap_in")

    # Tune the USRP by nRF24L channel number
    def set_channel(self, channel):

        new_channel = 2400e6 + channel * 1e6
        self.osmosdr_source.set_center_freq(2400e6 + channel * 1e6)
        self.nordic_rx.set_channel(channel)


# Microsoft mouse nordictap handler
class microsoft_nordictap_handler(gr.sync_block):

    def __init__(self, tb):
        gr.sync_block.__init__(
            self, name="Nordictap Handler", in_sig=None, out_sig=None)

        self.tb = tb
        self.message_port_register_in(pmt.intern("nordictap_in"))
        self.set_msg_handler(
            pmt.intern("nordictap_in"), self.nordictap_handler)

        # Tick / channel hopping state and logic
        self.last_rx = time.time()
        self.last_tune = time.time()
        self.ch_timeout = 0.4  # timeout a channel after 200ms
        self.last_ch = 0
        thread.start_new_thread(self.tick, ())

        # Channels and channel groups
        self.channels = [3, 29, 21, 5, 23, 17, 19, 50, 31, 25,
                         46, 27, 78, 70, 72, 44, 56, 48, 68, 80, 54, 52, 74, 76]
        self.channel_groups = []
        for x in range(6):
            chs = []
            for y in range(4):
                chs.append(self.channels[y * 6 + x])
            self.channel_groups.append(chs)

        # Discovered device state
        self.mouse_address = None

    # 10ms tick
    def tick(self):

        while True:

            # Check for a stale channel
            if ((time.time() - self.last_rx) > self.ch_timeout * 5) and  \
               ((time.time() - self.last_tune) > self.ch_timeout):

                self.last_ch += 1
                if self.last_ch >= len(self.channels):
                    self.last_ch = 0
                print 'Tuning to 24%02i MHz' % self.channels[self.last_ch]
                self.last_tune = time.time()
                self.tb.set_channel(self.channels[self.last_ch])

            # Wait 10ms
            time.sleep(0.01)

    def nordictap_handler(self, msg):

        data = pmt.to_python(msg).tostring()

        # Unpack the header
        values = struct.unpack('BBBBBBB', data[0:7])
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

        # Check for a Microsoft mouse
        if self.mouse_address is None:
            if ((ord(address[0]) & 0xF0) == 0xA0) and \
               ((ord(address[4]) & 0x0F) == 0x06) and \
               payload_length == 19:

                # Set the mouse address
                self.mouse_address = address

                # Set the channel group
                for x in range(6):
                    if channel in self.channel_groups[x]:
                        self.channels = self.channel_groups[x]
                        break

        # Camp on the channel and print out the packet if this is our target
        # device
        if self.mouse_address == address:

            self.last_rx = time.time()

            # Print the channel, sequence number, address and payload
            print 'CH=' + str(2400 + channel),
            print 'SEQ=' + str(sequence_number),
            print 'ADDR=' + ':'.join('%02X' % ord(b) for b in address),
            print 'PLD=' + ':'.join('%02X' % ord(b) for b in payload),
            print 'CRC=' + ':'.join('%02X' % ord(b) for b in crc)


def main():
    tb = top_block()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
