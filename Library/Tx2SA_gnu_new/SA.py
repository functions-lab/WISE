import argparse
import os

import sys
sys.path.append(os.path.dirname(__file__)+'/MBX')
from MBX.millibox import Millibox

parser = argparse.ArgumentParser(description='Spectrum Analyzer Measurement Script')
parser.add_argument('--csv', default='test', type=str,
    help='spectrum file path and name')
parser.add_argument('--device', default='USBDISK', type=str, choices=['USBDISK', 'SDCARD'],
    help='spectrum file path store device')
parser.add_argument('--carrier', default=1500000000, type=float,
    help='carrier frequency in [Hz]')
parser.add_argument('--band', default=50000000, type=float,
    help='monitored spectrum bandwidth in [Hz]')



if __name__ == "__main__":
    opt = parser.parse_args()
    CSV = opt.csv
    DEVICE = opt.device
    CARRIER = opt.carrier
    BAND = opt.band
    
    millibox = Millibox(addr='10.237.199.227')
    # millibox = Millibox(addr='10.237.194.114')

    millibox.Overview(carrier=CARRIER, band=BAND, rbw=5e3, fileName=CSV, device=DEVICE)
