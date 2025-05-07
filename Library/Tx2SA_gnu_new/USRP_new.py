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
parser.add_argument('--addr', default='192.168.10.2', type=str,
    help='USRP IP address')
parser.add_argument('--rate', default=1e6, type=int,
    help='Sampling rate in Hz for all the sub-devices')
parser.add_argument('--time', default=1.0, type=float,
    help='Time duration in s for all the sub-devices, -1 for infinity loop with key exit')
parser.add_argument('--clock', default=250e6, type=float,
    help='Clock frequency in Hz for all the sub-devices')
# TX 1
parser.add_argument('--fileTX_1', default='.', type=str,
    help='Binary file to load IQ samples for sub-device A:0, \'.\' for not used')
parser.add_argument('--freqTX_1', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device A:0')
parser.add_argument('--gainTX_1', default=20, type=float,
    help='Power gain in dB for sub-device A:0')
# TX 2
parser.add_argument('--fileTX_2', default='.', type=str,
    help='Binary file to load IQ samples for sub-device B:0, \'.\' for not used')
parser.add_argument('--freqTX_2', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device B:0')
parser.add_argument('--gainTX_2', default=20, type=float,
    help='Power gain in dB for sub-device B:0')
# TX 3
parser.add_argument('--fileTX_3', default='.', type=str,
    help='Binary file to load IQ samples for sub-device A:1, \'.\' for not used')
parser.add_argument('--freqTX_3', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device A:1')
parser.add_argument('--gainTX_3', default=20, type=float,
    help='Power gain in dB for sub-device A:1')
# TX 4
parser.add_argument('--fileTX_4', default='.', type=str,
    help='Binary file to load IQ samples for sub-device B:1, \'.\' for not used')
parser.add_argument('--freqTX_4', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device B:1')
parser.add_argument('--gainTX_4', default=20, type=float,
    help='Power gain in dB for sub-device B:1')
# RX 1
parser.add_argument('--fileRX_1', default='.', type=str,
    help='Binary file to save IQ samples for sub-device A:0, \'.\' for not used')
parser.add_argument('--freqRX_1', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device A:0')
parser.add_argument('--gainRX_1', default=10, type=float,
    help='Power gain in dB for sub-device A:0')
# RX 2
parser.add_argument('--fileRX_2', default='.', type=str,
    help='Binary file to load IQ samples for sub-device B:0, \'.\' for not used')
parser.add_argument('--freqRX_2', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device B:0')
parser.add_argument('--gainRX_2', default=10, type=float,
    help='Power gain in dB for sub-device B:0')
# RX 3
parser.add_argument('--fileRX_3', default='.', type=str,
    help='Binary file to save IQ samples for sub-device A:1, \'.\' for not used')
parser.add_argument('--freqRX_3', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device A:1')
parser.add_argument('--gainRX_3', default=10, type=float,
    help='Power gain in dB for sub-device A:1')
# RX 4
parser.add_argument('--fileRX_4', default='.', type=str,
    help='Binary file to load IQ samples for sub-device B:1, \'.\' for not used')
parser.add_argument('--freqRX_4', default=3e9, type=int,
    help='Carrier frequency in Hz for sub-device B:1')
parser.add_argument('--gainRX_4', default=10, type=float,
    help='Power gain in dB for sub-device B:1')



class USRP(gr.top_block):
    def __init__(self, opt):
        ADDR = opt.addr
        RATE = opt.rate
        CLOCK = opt.clock
        FILE_TX_1 = opt.fileTX_1 if opt.fileTX_1!='.' else ''
        FREQ_TX_1 = opt.freqTX_1
        GAIN_TX_1 = opt.gainTX_1
        FILE_TX_2 = opt.fileTX_2 if opt.fileTX_2!='.' else ''
        FREQ_TX_2 = opt.freqTX_2
        GAIN_TX_2 = opt.gainTX_2
        FILE_TX_3 = opt.fileTX_3 if opt.fileTX_3!='.' else ''
        FREQ_TX_3 = opt.freqTX_3
        GAIN_TX_3 = opt.gainTX_3
        FILE_TX_4 = opt.fileTX_4 if opt.fileTX_4!='.' else ''
        FREQ_TX_4 = opt.freqTX_4
        GAIN_TX_4 = opt.gainTX_4
        FILE_RX_1 = opt.fileRX_1 if opt.fileRX_1!='.' else ''
        FREQ_RX_1 = opt.freqRX_1
        GAIN_RX_1 = opt.gainRX_1
        FILE_RX_2 = opt.fileRX_2 if opt.fileRX_2!='.' else ''
        FREQ_RX_2 = opt.freqRX_2
        GAIN_RX_2 = opt.gainRX_2
        FILE_RX_3 = opt.fileRX_3 if opt.fileRX_3!='.' else ''
        FREQ_RX_3 = opt.freqRX_3
        GAIN_RX_3 = opt.gainRX_3
        FILE_RX_4 = opt.fileRX_4 if opt.fileRX_4!='.' else ''
        FREQ_RX_4 = opt.freqRX_4
        GAIN_RX_4 = opt.gainRX_4

        fileTxList = [FILE_TX_1, FILE_TX_2, FILE_TX_3, FILE_TX_4]
        freqTxList = [FREQ_TX_1, FREQ_TX_2, FREQ_TX_3, FREQ_TX_4]
        gainTxList = [GAIN_TX_1, GAIN_TX_2, GAIN_TX_3, GAIN_TX_4]
        fileRxList = [FILE_RX_1, FILE_RX_2, FILE_RX_3, FILE_RX_4]
        freqRxList = [FREQ_RX_1, FREQ_RX_2, FREQ_RX_3, FREQ_RX_4]
        gainRxList = [GAIN_RX_1, GAIN_RX_2, GAIN_RX_3, GAIN_RX_4]

        subdevList = ['A:0', 'B:0', 'A:1', 'B:1']
        subdevNum = len(subdevList)

        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        # Configure TX
        subdevTx = ''
        fileTxNum = 0
        for subdevIdx in range(subdevNum):
            if len(fileTxList[subdevIdx]) > 0:
                fileTxNum += 1
                subdevTx += subdevList[subdevIdx] + ' '
        if fileTxNum > 0:
            self.uhd_usrp_sink = uhd.usrp_sink(
                ",".join(("addr0="+ADDR+",master_clock_rate="+str(CLOCK), '')),
                uhd.stream_args(cpu_format="fc32", args='', channels=list(range(0, fileTxNum))), "")
            self.uhd_usrp_sink.set_subdev_spec(subdevTx, 0)
            self.uhd_usrp_sink.set_samp_rate(RATE)
            self.uhd_usrp_sink.set_time_unknown_pps(uhd.time_spec(0))
            # self.uhd_usrp_sink.set_start_time(uhd.time_spec(1.0))

            fileTxIdx = -1
            for subdevIdx in range(subdevNum):
                if len(fileTxList[subdevIdx]) > 0:
                    fileTxIdx += 1

                    self.uhd_usrp_sink.set_center_freq(freqTxList[subdevIdx], fileTxIdx)
                    self.uhd_usrp_sink.set_antenna("TX/RX", fileTxIdx)
                    self.uhd_usrp_sink.set_gain(gainTxList[subdevIdx], fileTxIdx)

                    exec('self.blocks_file_source_'+str(subdevIdx)+' = blocks.file_source(gr.sizeof_gr_complex*1, fileTxList[subdevIdx], True, 0, 0)')
                    exec('self.blocks_file_source_'+str(subdevIdx)+'.set_begin_tag(pmt.PMT_NIL)')

                    exec('self.connect((self.blocks_file_source_'+str(subdevIdx)+', 0), (self.uhd_usrp_sink, fileTxIdx))')

        # Configure RX
        subdevRx = ''
        fileRxNum = 0
        for subdevIdx in range(subdevNum):
            if len(fileRxList[subdevIdx]) > 0:
                fileRxNum += 1
                subdevRx += subdevList[subdevIdx] + ' '
        if fileRxNum > 0:
            self.uhd_usrp_source = uhd.usrp_source(
                ",".join(("addr0="+ADDR+",master_clock_rate="+str(CLOCK), '')),
                uhd.stream_args(cpu_format="fc32", args='', channels=list(range(0, fileRxNum))))
            self.uhd_usrp_source.set_subdev_spec(subdevRx, 0)
            self.uhd_usrp_source.set_samp_rate(RATE)
            self.uhd_usrp_source.set_time_unknown_pps(uhd.time_spec(0))
            # self.uhd_usrp_source.set_start_time(uhd.time_spec(1.0))

            fileRxIdx = -1
            for subdevIdx in range(subdevNum):
                if len(fileRxList[subdevIdx]) > 0:
                    fileRxIdx += 1

                    self.uhd_usrp_source.set_center_freq(freqRxList[subdevIdx], fileRxIdx)
                    self.uhd_usrp_source.set_antenna("RX2", fileRxIdx)
                    self.uhd_usrp_source.set_gain(gainRxList[subdevIdx], fileRxIdx)

                    exec('self.blocks_file_sink_'+str(subdevIdx)+' = blocks.file_sink(gr.sizeof_gr_complex*1, fileRxList[subdevIdx], False)')
                    exec('self.blocks_file_sink_'+str(subdevIdx)+'.set_unbuffered(False)')
                    
                    exec('self.connect((self.uhd_usrp_source, fileRxIdx), (self.blocks_file_sink_'+str(subdevIdx)+', 0))')



def main(top_block_cls=USRP, options=None):
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
