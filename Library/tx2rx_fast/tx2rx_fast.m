function [packetRx, snr] = tx2rx_fast(packet_1, packet_2, shrink, freq, param)
    % for odd input size and even output size:
    % carrierRx = param.carrierRx - 3*freq;
    % for odd input size and odd output size:
    % NOT Supported!

    power_1 = param.powerRF - param.atten;
    power_2 = param.powerLO;
    insertion = param.insertion;
    boltzmann = param.boltzmann;
    temperature = param.temperature;
    noisefigure = param.noisefigure;

    sampleRateTx = param.sampleRate;
    sampleRateRx = param.sampleRate / shrink;
    upsample = 2;
    padLen = 100 * shrink; % max(round(0.5*length(packet_1)), 1000);
    padTx = zeros(1, padLen);
    waveAxis = (1: upsample*length(packet_1)) /upsample/sampleRateTx;
    padAxis = (1: upsample*padLen) /upsample/sampleRateTx;

    [wave_1, pad_1] = AddNoise(packet_1, padTx, power_1, sampleRateTx, param);
    wave_1 = upsampling(wave_1, sampleRateTx, upsample*sampleRateTx);
    pad_1 = upsampling(pad_1, sampleRateTx, upsample*sampleRateTx);
    [wave_2, pad_2] = AddNoise(packet_2, padTx, power_2, sampleRateTx, param);
    wave_2 = upsampling(wave_2, sampleRateTx, upsample*sampleRateTx);
    pad_2 = upsampling(pad_2, sampleRateTx, upsample*sampleRateTx);
    if param.convert == "up"
        waveRx = wave_1 .* wave_2 .* exp(-1i*2*pi*freq*waveAxis);
        padRx = pad_1 .* pad_2 .* exp(-1i*2*pi*freq*padAxis);
    else
        waveRx = wave_1 .* conj(wave_2) .* exp(-1i*2*pi*freq*waveAxis);
        padRx = pad_1 .* pad_2 .* exp(-1i*2*pi*freq*padAxis);
    end
    powerRx = power_1 - insertion - noisefigure;
    [waveRx, padRx] = AddNoise(waveRx, padRx, powerRx, upsample*sampleRateTx, param);
    waveRx = myFilter(waveRx, sampleRateRx, upsample*sampleRateTx);
    padRx = myFilter(padRx, sampleRateRx, upsample*sampleRateTx);
    waveRx = waveRx(upsample*shrink: upsample*shrink: end);
    padRx = padRx(upsample*shrink: upsample*shrink: end);
    packetRx = waveRx;
    wavePower = GetEnergy(waveRx);
    padPower = GetEnergy(padRx);

%     Clear Version
%     [waveLow_1, padLow_1] = AddNoise(packet_1, padTx, power_1, sampleRateTx, param);
%     waveHigh_1 = upsampling(waveLow_1, sampleRateTx, upsample*sampleRateTx);
%     padHigh_1 = upsampling(padLow_1, sampleRateTx, upsample*sampleRateTx);
%     [waveLow_2, padLow_2] = AddNoise(packet_2, padTx, power_2, sampleRateTx, param);
%     waveHigh_2 = upsampling(waveLow_2, sampleRateTx, upsample*sampleRateTx);
%     padHigh_2 = upsampling(padLow_2, sampleRateTx, upsample*sampleRateTx);
%     if param.convert == "up"
%         waveHigh_Rx = waveHigh_1 .* waveHigh_2 .* exp(-1i*2*pi*freq*waveAxis);
%         padHigh_Rx = padHigh_1 .* padHigh_2 .* exp(-1i*2*pi*freq*padAxis);
%     else
%         waveHigh_Rx = waveHigh_1 .* conj(waveHigh_2) .* exp(-1i*2*pi*freq*waveAxis);
%         padHigh_Rx = padHigh_1 .* padHigh_2 .* exp(-1i*2*pi*freq*padAxis);
%     end
%     powerRx = power_1 - insertion;
%     [waveNoise_Rx, padNoise_Rx] = AddNoise(waveHigh_Rx, padHigh_Rx, powerRx, upsample*sampleRateTx, param);
%     waveFilter_Rx = myFilter(waveNoise_Rx, sampleRateRx, upsample*sampleRateTx);
%     padFilter_Rx = myFilter(padNoise_Rx, sampleRateRx, upsample*sampleRateTx);
%     waveLow_Rx = waveFilter_Rx(upsample*shrink: upsample*shrink: end);
%     padLow_Rx = padFilter_Rx(upsample*shrink: upsample*shrink: end);
%     powerLow = powerRx + 10*log10(GetEnergy(waveFilter_Rx)/GetEnergy(waveNoise_Rx)) - 10*log10(10^(noisefigure/10)-1);
%     [waveFig_Rx, padFig_Rx] = AddNoise(waveLow_Rx, padLow_Rx, powerLow, sampleRateRx, param);
%     packetRx = waveFig_Rx;
%     wavePower = GetEnergy(waveFig_Rx);
%     padPower = GetEnergy(padFig_Rx);

    if wavePower <= padPower
        snr = power_1 - insertion - noisefigure - 10*log10(boltzmann*temperature*sampleRateTx) - 30; % approximation without TX noise
    else
        snr = 10*log10((wavePower-padPower)/padPower);
    end
end

function [signalOut, noiseOut] = AddNoise(signalIn, noiseIn, power, sampleRate, param)
    boltzmann = param.boltzmann;
    temperature = param.temperature;

    snr = 10^((power-30)/10) / (boltzmann*temperature*sampleRate);
    sigma = GetEnergy(signalIn) / snr;
    signalOut = signalIn + randn(1, length(signalIn))*sqrt(sigma/2) + 1i*randn(1, length(signalIn))*sqrt(sigma/2);
    noiseOut = noiseIn + randn(1, length(noiseIn))*sqrt(sigma/2) + 1i*randn(1, length(noiseIn))*sqrt(sigma/2);
end

function [waveHigh] = upsampling(waveLow, rateLow, rateHigh)
    waveLenLow = length(waveLow);
    time = waveLenLow / rateLow;
    waveLenHigh = round(time*rateHigh);

    specLow = fft(waveLow) * rateHigh / rateLow;
    if mod(waveLenLow, 2) == 1
        mid = (waveLenLow+1)/2;
    else
        mid = waveLenLow / 2;
    end
    specHigh = zeros(1, waveLenHigh);
    specHigh(1: mid) = specLow(1: mid);
    specHigh(waveLenHigh-waveLenLow+mid+1: end) = specLow(mid+1: end);
    waveHigh = ifft(specHigh);
end

function [waveOut] = myFilter(waveIn, freqLow, freqHigh)
    ratio = freqLow / freqHigh;
    mask = zeros(1, length(waveIn));
    mask(1: ceil(length(waveIn)*ratio/2)) = 1;
    mask(end-floor(length(waveIn)*ratio/2)+1: end) = 1;

    specIn = fft(waveIn);
    specOut = specIn .* mask;
    waveOut = ifft(specOut);
end