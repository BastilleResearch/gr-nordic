#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.8.2.0

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
from gnuradio import eng_notation
from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
import nordic
import time
import threading

from gnuradio import qtgui

class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
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

        self.settings = Qt.QSettings("GNU Radio", "top_block")

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
        self.probe_var = probe_var = 0
        self.payload = payload = "    20.0"
        self.address = address = [0, 85, 2, 5, 8, 0, 0, 2, 85, 85, 85, 85, 85]
        self.variable_qtgui_entry_0 = variable_qtgui_entry_0 = probe_var
        self.samp_rate = samp_rate = 32000
        self.pkt_vec = pkt_vec = address + [ ord(x) for x in payload ]

        ##################################################
        # Blocks
        ##################################################
        self.probe_signal = blocks.probe_signal_b()
        self._variable_qtgui_entry_0_tool_bar = Qt.QToolBar(self)
        self._variable_qtgui_entry_0_tool_bar.addWidget(Qt.QLabel('variable_qtgui_entry_0' + ": "))
        self._variable_qtgui_entry_0_line_edit = Qt.QLineEdit(str(self.variable_qtgui_entry_0))
        self._variable_qtgui_entry_0_tool_bar.addWidget(self._variable_qtgui_entry_0_line_edit)
        self._variable_qtgui_entry_0_line_edit.returnPressed.connect(
            lambda: self.set_variable_qtgui_entry_0(int(str(self._variable_qtgui_entry_0_line_edit.text()))))
        self.top_grid_layout.addWidget(self._variable_qtgui_entry_0_tool_bar)
        def _probe_var_probe():
            while True:

                val = self.probe_signal.level()
                try:
                    self.set_probe_var(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (10))
        _probe_var_thread = threading.Thread(target=_probe_var_probe)
        _probe_var_thread.daemon = True
        _probe_var_thread.start()

        self.nordic_nordictap_transmitter_0 = nordic.nordictap_transmitter(1, '\x55\x55\x55\x55\x55', '\x20\x20\x20\x20\x32\x30\x2E\x30', 0, 0)
        self.nordic_nordic_tx_0 = nordic.nordic_tx(1)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_message_strobe_1 = blocks.message_strobe(pmt.intern("trig"), 2000)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_1, 'strobe'), (self.nordic_nordictap_transmitter_0, 'trig'))
        self.msg_connect((self.nordic_nordictap_transmitter_0, 'nordictap_out'), (self.nordic_nordic_tx_0, 'nordictap_in'))
        self.connect((self.blocks_throttle_0, 0), (self.probe_signal, 0))
        self.connect((self.nordic_nordic_tx_0, 0), (self.blocks_throttle_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_probe_var(self):
        return self.probe_var

    def set_probe_var(self, probe_var):
        self.probe_var = probe_var
        self.set_variable_qtgui_entry_0(self.probe_var)

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

    def get_variable_qtgui_entry_0(self):
        return self.variable_qtgui_entry_0

    def set_variable_qtgui_entry_0(self, variable_qtgui_entry_0):
        self.variable_qtgui_entry_0 = variable_qtgui_entry_0
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_entry_0_line_edit, "setText", Qt.Q_ARG("QString", str(self.variable_qtgui_entry_0)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_pkt_vec(self):
        return self.pkt_vec

    def set_pkt_vec(self, pkt_vec):
        self.pkt_vec = pkt_vec





def main(top_block_cls=top_block, options=None):

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
