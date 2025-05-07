#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.8.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time



class default(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
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

        self.settings = Qt.QSettings("GNU Radio", "default")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", 'addr=192.168.10.2')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,4)),
            ),
        )
        self.uhd_usrp_source_0.set_subdev_spec('A:0 B:0 A:1 B:1', 0)
        self.uhd_usrp_source_0.set_samp_rate(1e6)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(2e9, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_gain(10, 0)

        self.uhd_usrp_source_0.set_center_freq(2e9, 1)
        self.uhd_usrp_source_0.set_antenna("RX2", 1)
        self.uhd_usrp_source_0.set_gain(10, 1)

        self.uhd_usrp_source_0.set_center_freq(2e9, 2)
        self.uhd_usrp_source_0.set_antenna("RX2", 2)
        self.uhd_usrp_source_0.set_gain(10, 2)

        self.uhd_usrp_source_0.set_center_freq(2e9, 3)
        self.uhd_usrp_source_0.set_antenna("RX2", 3)
        self.uhd_usrp_source_0.set_gain(10, 3)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", 'addr=192.168.10.2')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,4)),
            ),
            "",
        )
        self.uhd_usrp_sink_0.set_subdev_spec('A:0 B:0 A:1 B:1', 0)
        self.uhd_usrp_sink_0.set_samp_rate(1e6)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_sink_0.set_center_freq(2e9, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(10, 0)

        self.uhd_usrp_sink_0.set_center_freq(2e9, 1)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 1)
        self.uhd_usrp_sink_0.set_gain(10, 1)

        self.uhd_usrp_sink_0.set_center_freq(2e9, 2)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 2)
        self.uhd_usrp_sink_0.set_gain(10, 2)

        self.uhd_usrp_sink_0.set_center_freq(2e9, 3)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 3)
        self.uhd_usrp_sink_0.set_gain(10, 3)
        self.blocks_file_source_0_2 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/TX_3.bin', True, 0, 0)
        self.blocks_file_source_0_2.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/TX_4.bin', True, 0, 0)
        self.blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/TX_2.bin', True, 0, 0)
        self.blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/TX_1.bin', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0_2 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/RX_2.bin', False)
        self.blocks_file_sink_0_2.set_unbuffered(False)
        self.blocks_file_sink_0_1 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/RX_3.bin', False)
        self.blocks_file_sink_0_1.set_unbuffered(False)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/RX_4.bin', False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/zg88/CEI/Analog/Code/Library/tx2rx_gnu/gnuradio/RX_1.bin', False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_file_source_0_0, 0), (self.uhd_usrp_sink_0, 1))
        self.connect((self.blocks_file_source_0_1, 0), (self.uhd_usrp_sink_0, 3))
        self.connect((self.blocks_file_source_0_2, 0), (self.uhd_usrp_sink_0, 2))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 3), (self.blocks_file_sink_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 2), (self.blocks_file_sink_0_1, 0))
        self.connect((self.uhd_usrp_source_0, 1), (self.blocks_file_sink_0_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "default")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate




def main(top_block_cls=default, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
