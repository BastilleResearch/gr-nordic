#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Nrf Foo
# GNU Radio version: v3.8.2.0-101-g57a4df75

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
import pmt
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import iio
import nordic
import foo

from gnuradio import qtgui

class tx_nrf_foo(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Tx Nrf Foo")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Tx Nrf Foo")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "tx_nrf_foo")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.symbol_rate = symbol_rate = 2e6
        self.samp_rate = samp_rate = 4e6
        self.payload = payload = "22.75"
        self.address = address = [0, 120, 2, 5, 8, 2, 0, 2, 231, 231, 231, 231, 231]
        self.taps = taps = firdes.low_pass(1.0, samp_rate, (symbol_rate/2)*1.5,250e3, firdes.WIN_HAMMING, 6.76)
        self.pkt_vec = pkt_vec = address + [ ord(x) for x in payload ]
        self.freq = freq = 2520e6

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.pfb_synthesizer_ccf_0 = filter.pfb_synthesizer_ccf(
            1,
            taps,
            False)
        self.pfb_synthesizer_ccf_0.set_channel_map([])
        self.pfb_synthesizer_ccf_0.declare_sample_delay(0)
        self.nordic_nordic_tx_0 = nordic.nordic_tx(1)
        self.iio_pluto_sink_0 = iio.pluto_sink('ip:192.168.2.1', int(freq), int(samp_rate), 2000000, 0x200, False, 10.0, '', True)
        self.foo_burst_tagger_0 = foo.burst_tagger(pmt.intern("packet_len"), int(8*samp_rate/symbol_rate))
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
            samples_per_symbol=2,
            sensitivity=1.5707/2,
            bt=0.5,
            verbose=False,
            log=False)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.init_u8vector( len(pkt_vec),  pkt_vec), 1000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.nordic_nordic_tx_0, 'nordictap_in'))
        self.connect((self.digital_gfsk_mod_0, 0), (self.foo_burst_tagger_0, 0))
        self.connect((self.foo_burst_tagger_0, 0), (self.pfb_synthesizer_ccf_0, 0))
        self.connect((self.nordic_nordic_tx_0, 0), (self.digital_gfsk_mod_0, 0))
        self.connect((self.pfb_synthesizer_ccf_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.pfb_synthesizer_ccf_0, 0), (self.qtgui_time_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "tx_nrf_foo")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.set_taps(firdes.low_pass(1.0, self.samp_rate, (self.symbol_rate/2)*1.5, 250e3, firdes.WIN_HAMMING, 6.76))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_taps(firdes.low_pass(1.0, self.samp_rate, (self.symbol_rate/2)*1.5, 250e3, firdes.WIN_HAMMING, 6.76))
        self.iio_pluto_sink_0.set_params(int(self.freq), int(self.samp_rate), 2000000, 10.0, '', True)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_payload(self):
        return self.payload

    def set_payload(self, payload):
        self.payload = payload
        self.set_pkt_vec(self.address + [ ord(x) for x in self.payload ])

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address
        self.set_pkt_vec(self.address + [ ord(x) for x in self.payload ])

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.pfb_synthesizer_ccf_0.set_taps(self.taps)

    def get_pkt_vec(self):
        return self.pkt_vec

    def set_pkt_vec(self, pkt_vec):
        self.pkt_vec = pkt_vec
        self.blocks_message_strobe_0.set_msg(pmt.init_u8vector( len(self.pkt_vec),  self.pkt_vec))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.iio_pluto_sink_0.set_params(int(self.freq), int(self.samp_rate), 2000000, 10.0, '', True)





def main(top_block_cls=tx_nrf_foo, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
