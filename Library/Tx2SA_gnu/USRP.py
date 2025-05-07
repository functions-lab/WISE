#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.6.0

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time

import argparse
parser = argparse.ArgumentParser(description='Zhihui\'s USRP Control Script')
parser.add_argument('--addr', default='192.168.70.3', type=str,
    help='USRP IP address')
parser.add_argument('--rate', default=25e6, type=int,
    help='Sampling rate in Hz for both channels')
parser.add_argument('--time', default=1.0, type=float,
    help='Time duration in s for both channels, -1 for infinity loop with key exit')
# TX 1
parser.add_argument('--fileTX_1', default='.', type=str,
    help='Binary file to load IQ samples for channel A, \'.\' for not used')
parser.add_argument('--freqTX_1', default=3e9, type=int,
    help='Carrier frequency in Hz for channel A')
parser.add_argument('--gainTX_1', default=20, type=float,
    help='Power gain in dB for channel A')
# TX 2
parser.add_argument('--fileTX_2', default='.', type=str,
    help='Binary file to load IQ samples for channel B, \'.\' for not used')
parser.add_argument('--freqTX_2', default=3e9, type=int,
    help='Carrier frequency in Hz for channel B')
parser.add_argument('--gainTX_2', default=20, type=float,
    help='Power gain in dB for channel B')
# RX 1
parser.add_argument('--fileRX_1', default='.', type=str,
    help='Binary file to save IQ samples for channel A, \'.\' for not used')
parser.add_argument('--freqRX_1', default=3e9, type=int,
    help='Carrier frequency in Hz for channel A')
parser.add_argument('--gainRX_1', default=10, type=float,
    help='Power gain in dB for channel A')
# RX 2
parser.add_argument('--fileRX_2', default='.', type=str,
    help='Binary file to load IQ samples for channel B, \'.\' for not used')
parser.add_argument('--freqRX_2', default=3e9, type=int,
    help='Carrier frequency in Hz for channel B')
parser.add_argument('--gainRX_2', default=10, type=float,
    help='Power gain in dB for channel B')

class Radar(gr.top_block):

    def __init__(self, opt):
        ADDR = opt.addr
        RATE = opt.rate
        FILE_TX_1 = opt.fileTX_1 if opt.fileTX_1!='.' else ''
        FREQ_TX_1 = opt.freqTX_1
        GAIN_TX_1 = opt.gainTX_1
        FILE_TX_2 = opt.fileTX_2 if opt.fileTX_2!='.' else ''
        FREQ_TX_2 = opt.freqTX_2
        GAIN_TX_2 = opt.gainTX_2
        FILE_RX_1 = opt.fileRX_1 if opt.fileRX_1!='.' else ''
        FREQ_RX_1 = opt.freqRX_1
        GAIN_RX_1 = opt.gainRX_1
        FILE_RX_2 = opt.fileRX_2 if opt.fileRX_2!='.' else ''
        FREQ_RX_2 = opt.freqRX_2
        GAIN_RX_2 = opt.gainRX_2

        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        # Configure TX
        fileTxNum = int(len(FILE_TX_1)>0) + int(len(FILE_TX_2)>0)
        if fileTxNum > 0:
            if fileTxNum == 2:
                subdevTx = 'A:0 B:0'
            else:
                subdevTx = 'A:0' if int(len(FILE_TX_1)>0) else 'B:0'

            self.uhd_usrp_sink = uhd.usrp_sink(
                ",".join(("", "addr="+ADDR)),
                uhd.stream_args(cpu_format="fc32", args='', channels=list(range(0, fileTxNum))), "")
            self.uhd_usrp_sink.set_subdev_spec(subdevTx, 0)
            self.uhd_usrp_sink.set_samp_rate(RATE)
            self.uhd_usrp_sink.set_time_unknown_pps(uhd.time_spec(0))
            # self.uhd_usrp_sink.set_start_time(uhd.time_spec(1.0))

            fileTxIdx = -1
            if len(FILE_TX_1) > 0:
                fileTxIdx += 1

                self.uhd_usrp_sink.set_center_freq(FREQ_TX_1, fileTxIdx)
                self.uhd_usrp_sink.set_antenna("TX/RX", fileTxIdx)
                self.uhd_usrp_sink.set_gain(GAIN_TX_1, fileTxIdx)

                self.blocks_file_source_1 = blocks.file_source(gr.sizeof_gr_complex*1, FILE_TX_1, True, 0, 0)
                self.blocks_file_source_1.set_begin_tag(pmt.PMT_NIL)

                self.connect((self.blocks_file_source_1, 0), (self.uhd_usrp_sink, fileTxIdx))

            if len(FILE_TX_2) > 0:
                fileTxIdx += 1

                self.uhd_usrp_sink.set_center_freq(FREQ_TX_2, fileTxIdx)
                self.uhd_usrp_sink.set_antenna("TX/RX", fileTxIdx)
                self.uhd_usrp_sink.set_gain(GAIN_TX_2, fileTxIdx)

                self.blocks_file_source_2 = blocks.file_source(gr.sizeof_gr_complex*1, FILE_TX_2, True, 0, 0)
                self.blocks_file_source_2.set_begin_tag(pmt.PMT_NIL)

                self.connect((self.blocks_file_source_2, 0), (self.uhd_usrp_sink, fileTxIdx))

        # Configure RX
        fileRxNum = int(len(FILE_RX_1)>0) + int(len(FILE_RX_2)>0)
        if fileRxNum > 0:
            if fileRxNum == 2:
                subdevRx = 'A:0 B:0'
            else:
                subdevRx = 'A:0' if int(len(FILE_RX_1)>0) else 'B:0'

            self.uhd_usrp_source = uhd.usrp_source(
                ",".join(("", "addr="+ADDR)),
                uhd.stream_args(cpu_format="fc32", args='', channels=list(range(0, fileRxNum))))
            self.uhd_usrp_source.set_subdev_spec(subdevRx, 0)
            self.uhd_usrp_source.set_samp_rate(RATE)
            self.uhd_usrp_source.set_time_unknown_pps(uhd.time_spec(0))
            # self.uhd_usrp_source.set_start_time(uhd.time_spec(1.0))

            fileRxIdx = -1
            if len(FILE_RX_1) > 0:
                fileRxIdx += 1

                self.uhd_usrp_source.set_center_freq(FREQ_RX_1, fileRxIdx)
                self.uhd_usrp_source.set_antenna("RX2", fileRxIdx)
                self.uhd_usrp_source.set_gain(GAIN_RX_1, fileRxIdx)

                self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*1, FILE_RX_1, False)
                self.blocks_file_sink_1.set_unbuffered(False)

                self.connect((self.uhd_usrp_source, fileRxIdx), (self.blocks_file_sink_1, 0))

            if len(FILE_RX_2) > 0:
                fileRxIdx += 1

                self.uhd_usrp_source.set_center_freq(FREQ_RX_2, fileRxIdx)
                self.uhd_usrp_source.set_antenna("RX2", fileRxIdx)
                self.uhd_usrp_source.set_gain(GAIN_RX_2, fileRxIdx)
                
                self.blocks_file_sink_2 = blocks.file_sink(gr.sizeof_gr_complex*1, FILE_RX_2, False)
                self.blocks_file_sink_2.set_unbuffered(False)
                
                self.connect((self.uhd_usrp_source, fileRxIdx), (self.blocks_file_sink_2, 0))



def main(top_block_cls=Radar, options=None):
    opt = parser.parse_args()
    TIME = opt.time

    tb = top_block_cls(opt)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    if TIME > 0:
        time.sleep(TIME)
    else:
        try:
            input('Press Enter to quit: ')
        except EOFError:
            pass
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    main()
