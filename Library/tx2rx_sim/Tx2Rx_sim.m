function [packetRx, snr] = Tx2Rx_sim(packet_1, packet_2, shrink, freq, param)
    % for odd input size and even output size: 
    % carrierRx = param.carrierRx - 3*freq;
    % for odd input size and odd output size:
    % NOT Supported!

    packetNorm_1 = packet_1; %  / sqrt(GetEnergy(packet_1));
    packetNorm_2 = packet_2; %  / sqrt(GetEnergy(packet_2));
    [packetRx, mixerGain] = Tx2Rx_sim_core(packetNorm_1, packetNorm_2, nan, shrink, freq, param);
    disp(mixerGain);
    padLen = 100 * shrink;
    padding = zeros(1, padLen);
    [paddingRx, ~] = Tx2Rx_sim_core(padding, padding, mixerGain, shrink, freq, param);

    noisePower = GetEnergy(paddingRx);
    signalPower = GetEnergy(packetRx) - noisePower;
    snr = 10 * log10(signalPower/noisePower);
end

function [packet_Rx, mixerGain] = Tx2Rx_sim_core(packet_1, packet_2, mixerGain, shrink, freq, param)
    sampleRateTx = param.sampleRate;
    sampleRateRx = param.sampleRate / shrink;
    carrier_1 = param.carrierTx(1);
    carrier_2 = param.carrierTx(2);
    carrierRx = param.carrierRx - freq;

    resolution = round(param.analog/sampleRateTx);
    power_1 = param.powerRF;
    power_2 = param.powerLO;
    insertion = param.insertion;

    if length(packet_1) ~= length(packet_2)
        disp("Warning: Packet Lengths NOT Matched!");
    end
    packetLen_Tx = min(length(packet_1), length(packet_2));
    packetAxis_Tx = (1: packetLen_Tx) / sampleRateTx;
    packetLen_Rx = round(packetLen_Tx/shrink);
    packetAxis_Rx = (1: packetLen_Rx) / sampleRateRx;
    waveLen = min(length(packet_1), length(packet_2)) * resolution;
    waveAxis = (1: waveLen) / resolution / sampleRateTx;
    LOcos_1 = cos(2*pi*carrier_1*waveAxis);
    LOsin_1 = sin(2*pi*carrier_1*waveAxis);
    LOcos_2 = cos(2*pi*carrier_2*waveAxis);
    LOsin_2 = sin(2*pi*carrier_2*waveAxis);
    LOcos_Rx = cos(2*pi*carrierRx*waveAxis);
    LOsin_Rx = sin(2*pi*carrierRx*waveAxis);

    impedance = param.impedance;
    boltzmann = param.boltzmann;
    temperature = param.temperature;

    mixer = sqrt(10^(-insertion/10) / (impedance*10^(power_2/10)/1000));

    % Transmit the signal
    waveBase_1 = upsampling(packet_1, sampleRateTx, sampleRateTx*resolution);
    waveNorm_1 = waveBase_1 ./ sqrt(GetEnergy(waveBase_1)) * sqrt(impedance*10^(power_1/10)/1000);
    waveRF_1 = sqrt(2) * real(waveNorm_1 .* exp(1i*2*pi*carrier_1*waveAxis));

    waveBase_2 = upsampling(packet_2, sampleRateTx, sampleRateTx*resolution);
    waveNorm_2 = waveBase_2 ./ sqrt(GetEnergy(waveBase_2)) * sqrt(impedance*10^(power_2/10)/1000);
    waveRF_2 = sqrt(2) * real(waveNorm_2 .* exp(1i*2*pi*carrier_2*waveAxis));





%     packetPure_1 = real(packet_1 .* exp(1i*2*pi*carrier_1*packetAxis_Tx));
%     packetNorm_1 = packetPure_1 / sqrt(GetEnergy(packetPure_1)) * sqrt(impedance*10^(power_1/10)/1000);
%     packetNoise_1 = packetNorm_1 + randn(1, packetLen_Tx) * impedance*boltzmann*temperature*sampleRateTx;
%     wave_1 = upsampling(packetNoise_1, sampleRateTx, sampleRateTx*resolution);
% 
%     packetPure_2 = real(packet_2 .* exp(1i*2*pi*carrier_2*packetAxis_Tx));
%     packetNorm_2 = packetPure_2 / sqrt(GetEnergy(packetPure_2)) * sqrt(impedance*10^(power_2/10)/1000);
%     packetNoise_2 = packetNorm_2 + randn(1, packetLen_Tx) * impedance*boltzmann*temperature*sampleRateTx;
%     wave_2 = upsampling(packetNoise_2, sampleRateTx, sampleRateTx*resolution);

    % up/down conversion power split compensation?
    wavePure_Rx = waveRF_1 .* waveRF_2;
    waveNorm_Rx = mixer * wavePure_Rx;
    waveNoise_Rx = waveNorm_Rx + randn(1, waveLen) * impedance*boltzmann*temperature*sampleRateTx*resolution;

    waveBase_Rx = waveNoise_Rx .* exp(1i*2*pi*carrierRx*waveAxis);
    waveFilter_Rx = myFilter(waveBase_Rx, sampleRateRx, sampleRateTx*resolution);
    packet_Rx = waveFilter_Rx(resolution*shrink: resolution*shrink: end);
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