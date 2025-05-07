function [waveRx] = Simulation(wave_1, wave_2, param)
    sampleRate = param.sampleRate;
    waveLenLow = param.waveLen;
    analog = param.analog;
    beta = param.beta;
    carrier_1 = param.carrier_1;
    carrier_2 = param.carrier_2;
    carrierRx = param.carrierRx;

    waveLenHigh = round(waveLenLow/sampleRate*analog);
    timeAxis = (1: waveLenHigh)/analog;
    LOcos_1 = cos(2*pi*carrier_1*timeAxis);
    LOsin_1 = sin(2*pi*carrier_1*timeAxis);
    LOcos_2 = cos(2*pi*carrier_2*timeAxis);
    LOsin_2 = sin(2*pi*carrier_2*timeAxis);
    LORxcos = cos(2*pi*carrierRx*timeAxis);
    LORxsin = sin(2*pi*carrierRx*timeAxis);

    waveBase_1 = upsampling(wave_1, sampleRate, analog);
    waveHigh_1 = real(waveBase_1).*LOcos_1 + imag(waveBase_1).*LOsin_1;
    waveBase_2 = upsampling(wave_2, sampleRate, analog);
    waveHigh_2 = real(waveBase_2).*LOcos_2 + imag(waveBase_2).*LOsin_2;

    waveMix = (waveHigh_1 + waveHigh_2) + 10^(beta/20)*1/2*(waveHigh_1 + waveHigh_2).^2;

    waveRxBase = LORxcos .* waveMix + 1i*LORxsin .* waveMix;
    waveRxFilter = lowpass(waveRxBase, sampleRate/2, analog, 'Steepness', 0.95, 'StopbandAttenuation', 100);
    waveRx = waveRxFilter(round((1: waveLenLow)*analog/sampleRate));
end