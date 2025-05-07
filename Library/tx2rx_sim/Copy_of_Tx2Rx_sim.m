function [packetRx, snr] = Tx2Rx_sim(packet_1, packet_2, shrink, freq, param)
    % for odd input size and even output size: 
    % carrierRx = param.carrierRx - 3*freq;
    % for odd input size and odd output size:
    % NOT Supported!

    disp(sqrt(10^((param.powerLO-30)/10)*param.impedance));

    packetNorm_1 = packet_1 / sqrt(GetEnergy(packet_1));
    packetNorm_2 = packet_2 / sqrt(GetEnergy(packet_2));
    [packetRx, mixerGain] = Tx2Rx_sim_core(packetNorm_1, packetNorm_2, nan, shrink, freq, param);
    disp(mixerGain);
    padLen = 100 * shrink;
    padding = zeros(1, padLen);
    [paddingRx, ~] = Tx2Rx_sim_core(padding, padding, mixerGain, shrink, freq, param);

    noisePower = GetEnergy(paddingRx);
    signalPower = GetEnergy(packetRx) - noisePower;
    snr = 10 * log10(signalPower/noisePower);
end

function [packetRx, mixerGain] = Tx2Rx_sim_core(packet_1, packet_2, mixerGain, shrink, freq, param)
    sampleRateTx = param.sampleRate;
    sampleRateRx = param.sampleRate / shrink;
    carrier_1 = param.carrierTx(1);
    carrier_2 = param.carrierTx(2);
    carrierRx = param.carrierRx - freq;

    resolution = round(param.analog/sampleRateTx);
    power_1 = param.powerRF;
    power_2 = param.powerLO;
    insertion = param.insertion - 10*log10(4); % 4 comes from the frequency peak division.

    if length(packet_1) ~= length(packet_2)
        disp("Warning: Packet Lengths NOT Matched!");
    end
    waveLen = min(length(packet_1), length(packet_2)) * resolution;
    timeAxis = (1: waveLen) / resolution / sampleRateTx;
    LOcos_1 = cos(2*pi*carrier_1*timeAxis);
    LOsin_1 = sin(2*pi*carrier_1*timeAxis);
    LOcos_2 = cos(2*pi*carrier_2*timeAxis);
    LOsin_2 = sin(2*pi*carrier_2*timeAxis);
    LOcos_Rx = cos(2*pi*carrierRx*timeAxis);
    LOsin_Rx = sin(2*pi*carrierRx*timeAxis);

    % Transmit the signal
    waveDigit_1 = AddNoise(packet_1, power_1, nan, sampleRateTx, param);
    waveAnal_1 = upsampling(waveDigit_1, sampleRateTx, sampleRateTx*resolution);
    waveRF_1 = real(waveAnal_1).*LOcos_1 + imag(waveAnal_1).*LOsin_1;
    waveDigit_2 = AddNoise(packet_2, power_2, nan, sampleRateTx, param);
    waveAnal_2 = upsampling(waveDigit_2, sampleRateTx, sampleRateTx*resolution);
    waveRF_2 = real(waveAnal_2).*LOcos_2 + imag(waveAnal_2).*LOsin_2;

    % up/down conversion power split compensation?
    [waveRF_Rx, mixerGain] = AddNoise(waveRF_1.*waveRF_2, power_1-insertion, mixerGain, sampleRateTx*resolution, param);

    waveAnal_Rx = LOcos_Rx .* waveRF_Rx + 1i*LOsin_Rx .* waveRF_Rx;
    waveFilter_Rx = myFilter(waveAnal_Rx, sampleRateRx, sampleRateTx*resolution);
    packetRx = waveFilter_Rx(resolution*shrink: resolution*shrink: end);
end

function [waveOut, gain] = AddNoise(waveIn, power, gain, bandwidth, param)
    impedance = param.impedance;
    boltzmann = param.boltzmann;
    temperature = param.temperature;

    noiseVolt = sqrt(boltzmann*temperature*bandwidth * impedance);
    waveVolt = sqrt(GetEnergy(waveIn));
    if isnan(gain)
        signalVolt = sqrt(10^((power-30)/10) * impedance);
        gain = signalVolt / waveVolt;
    end
    if waveVolt > 0
        waveOut = gain * waveIn + randn(1, length(waveIn)) * noiseVolt;
    else
        waveOut = randn(1, length(waveIn)) * noiseVolt;
    end
end

function [waveHigh] = upsampling(waveLow, rateLow, rateHigh)
    waveLenLow = length(waveLow);
    time = waveLenLow / rateLow;
    waveLenHigh = round(time*rateHigh);

    specLow = fft(waveLow);
    if mod(waveLenLow, 2) == 1
        mid = (waveLenLow+1)/2;
    else
        mid = waveLenLow / 2;
    end
    specLow_1 = specLow(1: mid);
    specLow_2 = specLow(mid+1: end);

    specHigh = [specLow_1 zeros(1, waveLenHigh-waveLenLow) specLow_2];
    waveHigh = ifft(specHigh) * rateHigh / rateLow;
end

function [waveOut] = myFilter(waveIn, freqLow, freqHigh)
    ratio = freqLow / freqHigh;
    baseLeft = ceil(length(waveIn) * ratio / 2);
    baseRight = floor(length(waveIn) * ratio / 2);

    specIn = fft(waveIn);
    specOut = zeros(1, length(waveIn));
    specOut(1: baseLeft) = specIn(1: baseLeft);
    specOut(end-baseRight+1: end) = specIn(end-baseRight+1: end);
    waveOut = ifft(specOut);
end