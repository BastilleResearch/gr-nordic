#!/usr/bin/python3

from gnuradio import gr, blocks, digital, filter, soapy, video_sdl
from gnuradio.filter import firdes

import threading
import nordic
import pmt
import struct
import time
import argparse
import numpy as np

WIDTH, HEIGHT = 1680,1050

class top_block(gr.top_block):

    def __init__(self,args):
        gr.top_block.__init__(self, "AirHogs Sync Framer Example")

        # SDR configuration
        self.freq = 2402e6
        self.gain = 70
        self.symbol_rate = 2e6
        self.sample_rate = 4e6

        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)

        self.soapy_hackrf_source_0.set_sample_rate(0, self.sample_rate)
        self.soapy_hackrf_source_0.set_bandwidth(0, 0)
        self.soapy_hackrf_source_0.set_frequency(0, self.freq)
        self.soapy_hackrf_source_0.set_gain(0, 'AMP', True)
        self.soapy_hackrf_source_0.set_gain(0, 'LNA', min(max(32, 0.0), 40.0))
        self.soapy_hackrf_source_0.set_gain(0, 'VGA', min(max(32, 0.0), 62.0))

        # Low pass filter
        self.lpf = filter.fir_filter_ccf(
            1, firdes.low_pass_2(1, self.sample_rate, self.symbol_rate / 2, 50e3, 50))

        # GFSK demod, defaults to 2 samples per symbol
        self.gfsk_demod = digital.gfsk_demod()

        # Nordic RX
        self.nordic_rx = nordic.nordic_rx(3, 5, 2, 2)

        # Video SDL
        fps = 15

        self.v2s = blocks.vector_to_stream(1,WIDTH)
        self.throttle_0 = blocks.throttle(gr.sizeof_char, fps*WIDTH*HEIGHT, True)
        self.video_sdl0 = video_sdl.sink_uc(fps,WIDTH,HEIGHT,0,WIDTH,HEIGHT)

        # Connect the blocks
        self.connect((self.soapy_hackrf_source_0, 0), (self.lpf, 0))
        self.connect((self.lpf, 0), (self.gfsk_demod, 0))
        self.connect((self.gfsk_demod, 0), (self.nordic_rx, 0))


        # Handle incoming packets
        self.nordictap_handler = microsoft_nordictap_handler(self,args.address)
        self.msg_connect(
            self.nordic_rx, "nordictap_out", self.nordictap_handler, "nordictap_in")

        self.connect((self.nordictap_handler, 0),(self.v2s,0))
#        self.connect((self.v2s, 0), (self.video_sdl0, 0)) # no throttle?
        self.connect((self.v2s, 0), (self.throttle_0, 0))
        self.connect((self.throttle_0, 0), (self.video_sdl0, 0))

    # Tune the USRP by nRF24L channel number
    def set_channel(self, channel):

        new_channel = 2400e6 + channel * 1e6
        self.soapy_hackrf_source_0.set_frequency(0,2400e6 + channel * 1e6)

# Microsoft mouse nordictap handler
class microsoft_nordictap_handler(gr.sync_block):

    def __init__(self, tb, address):
        gr.sync_block.__init__(
            self, name="Nordictap Handler", in_sig=None, out_sig=[np.dtype(f"{WIDTH}B") ])

        self.tb = tb
        self.address = address
        self.message_port_register_in(pmt.intern("nordictap_in"))
        self.set_msg_handler(
            pmt.intern("nordictap_in"), self.nordictap_handler)

        # Tick / channel hopping state and logic
        self.last_rx = time.time()
        self.last_tune = time.time()
        self.ch_timeout = 0.1  # timeout a channel after 200ms
        self.last_ch = 0

        # Channels and channel groups
        self.channels = range(0, 99)
        self.canvas = np.zeros((HEIGHT,WIDTH),dtype=np.uint8)
        self.xr = 400
        self.yr = 300
        self.hc = 0

        thr = threading.Thread(target = self.tick,)
        thr.start()

    # 10ms tick
    def tick(self):

        fade = 0

        while True:
            # Check for a stale channel
            if ((time.time() - self.last_rx) > self.ch_timeout * 25) and  \
               ((time.time() - self.last_tune) > self.ch_timeout):

                self.last_ch += 1
                if self.last_ch >= len(self.channels):
                    self.last_ch = 0
                print('T24%02i' % self.channels[self.last_ch])
                self.last_tune = time.time()
                self.tb.set_channel(self.channels[self.last_ch])

            # Wait 10ms
            time.sleep(0.01)
            fade += 1

            if fade > 5:
                self.canvas[np.where(self.canvas>1)] -= 1
                fade = 0

    def work(self,input_items, output_items):
        c = -1
        for c,(out, src) in enumerate(zip(output_items[0],self.canvas[self.hc%HEIGHT:])):
            out[:] = src

#        print(self.hc,output_items[0].shape,self.canvas[self.hc:].shape)
            
        self.hc += c+1
        return c+1
    
    def nordictap_handler(self, msg):

        data = pmt.to_python(msg).tostring()

        # Unpack the header
        values = struct.unpack('BBBBBBB', data[0:7])
        channel = self.last_ch
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
        
        if address.hex().startswith(self.address.lower()):
            self.last_rx = self.last_tune = time.time()

            if payload.startswith(b"\0\xc2"):
                b,xy = struct.unpack("xxbxIxx",payload)
                y = xy>>12
                x = xy&0xfff
                x = x-2**12 if x&2**11 else x
                y = y-2**12 if y&2**11 else y
                
                self.yr += y
                self.xr += x

                px = self.xr%WIDTH 
                py = self.yr%HEIGHT

                self.canvas[py-2:py+2,px-2:px+2] = 255 if b else 96

        # Print the channel, sequence number, address and payload
        # print(f"""CH={2400 + channel} SEQ={sequence_number} ADDR={address.hex()} PLD={payload.hex()} CRC={crc.hex()}""")
        """
bs = []
xs = []
ys = []

xsd = []
ysd = []

yr = 0
xr = 0

for line in map(lambda x:dict(map(lambda y:tuple(y.split("=")),x.split())),data):
    PLD = line.get("PLD")
    if PLD and PLD.startswith("00:C2"):
        b,xy = unpack("xxbxIxx",bytes.fromhex(PLD.replace(":","")))
        y = xy>>12
        x = xy&0xfff
        x = x-2**12 if x&2**11 else x
        y = y-2**12 if y&2**11 else y

        yr -= y
        xr += x

        if b:
            xs.append(xr)
            ys.append(yr)
        else:
            xsd.append(xr)
            ysd.append(yr)
            
        bs.append(b)
#        bytes = np.array(map(ord,bytes),dtype=np.uint8)
#        bits = np.unpackbits(bytes).reshape([len(bytes)*8])
#        print bits

plt.scatter(xs,ys,color="blue")
plt.scatter(xsd,ysd,alpha=0.1,color="red")
"""

def main():
    parser = argparse.ArgumentParser('Nordic Scanner Sniffer',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=120))
    parser.add_argument(
        '-a', '--address', type=str, help='hex adress', default="")

    args = parser.parse_args()

    tb = top_block(args)
    tb.start()
    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    main()
