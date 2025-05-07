import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import time

import mbx_instrument as SA



class Millibox():
    def __init__(self, addr='192.168.0.100'):
        super(Millibox, self).__init__()

        inst = SA.inst_setup(mode='SA', addr=['TCPIP0::'+addr+'::inst0::INSTR'])
        inst.init_meas()

        self.inst = inst

    def Overview(self, carrier, band, rbw=5e3, fileName=None, device='USBDISK'):
        inst = self.inst
        inst.set_rbw(rbw)
        inst.set_trace_number(int(band//rbw))
        inst.set_channel_power_band(band)
        inst.set_span(band)
        inst.set_freq(carrier)
        inst.set_RF_atten(20)
        
        time.sleep(10)
        
        if fileName is not None:
            inst.save_file(fileName, device=device)

    def Scan(self, carrier, band, toneList=[0], rbw=5e3, fileName=None, device='USBDISK'):
        inst = self.inst
        inst.set_rbw(rbw)
        inst.set_trace_number(int(band//rbw))
        inst.set_span(band*2)
        inst.set_channel_power_band(band)

        powerList = []
        for toneIdx in tqdm(range(len(toneList))):
            tone = toneList[toneIdx]
            
            freq = carrier + tone
            inst.set_freq(freq)
            time.sleep(1)
            power, _ = inst.get_channel_power()
            powerList.append(power)
            if fileName is not None:
                inst.save_file(fileName+'_'+str(toneIdx), device=device)
        
        return powerList
