function [packetRx, snr] = tx2rx_fast(packet_1, packet_2, shrink, freq, param)
    % for odd input size and even output size: 
    % carrierRx = param.carrierRx - 3*freq;
    % for odd input size and odd output size:
    % NOT Supported!

    power_1 = param.powerRF;
    power_2 = param.powerLO;
    insertion = param.insertion;

    sampleRateTx = param.sampleRate;
    sampleRateRx = param.sampleRate / shrink;
    upsample = 3;
    padLen = max(round(0.5*length(packet_1)), 1000);
    paddingTx = zeros(1, padLen);
    waveAxis = (1: upsample*length(packet_1)+upsample*padLen) /upsample/sampleRateTx;

    waveLow_1 = AddNoise([packet_1 paddingTx], length(packet_1), power_1, sampleRateTx, param);
    waveHigh_1 = upsampling(waveLow_1, sampleRateTx, upsample*sampleRateTx);
    waveLow_2 = AddNoise([packet_2 paddingTx], length(packet_1), power_2, sampleRateTx, param);
    waveHigh_2 = upsampling(waveLow_2, sampleRateTx, upsample*sampleRateTx);
    if param.convert == "up"
        waveHigh_Rx = waveHigh_1 .* waveHigh_2 .* exp(-1i*2*pi*freq*waveAxis);
    else
        waveHigh_Rx = waveHigh_1 .* conj(waveHigh_2) .* exp(-1i*2*pi*freq*waveAxis);
    end
    waveNoise_Rx = AddNoise(waveHigh_Rx, upsample*length(packet_1), power_1-insertion, upsample*sampleRateTx, param);
    waveFilter_Rx = myFilter(waveNoise_Rx, sampleRateRx, upsample*sampleRateTx);
    waveLow_Rx = waveFilter_Rx(upsample*shrink: upsample*shrink: end);
    
    packetRx = waveLow_Rx(1: round(length(packet_1)/shrink));
    paddingRx = waveLow_Rx(end-round(padLen*0.9/shrink)+1: end-round(padLen*0.1/shrink));
    snr = 10*log10(GetEnergy(packetRx) / GetEnergy(paddingRx));
end

function [waveOut] = AddNoise(waveIn, packetLen, power, sampleRate, param)
    boltzmann = param.boltzmann;
    temperature = param.temperature;

    snr = 10^((power-30)/10) / (boltzmann*temperature*sampleRate);
%     disp(10*log10(snr));
    sigma = GetEnergy(waveIn(1: packetLen)) / snr;
    waveOut = waveIn + randn(1, length(waveIn))*sqrt(sigma/2) + 1i*randn(1, length(waveIn))*sqrt(sigma/2);
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
    mask = zeros(1, length(waveIn));
    mask(1: ceil(length(waveIn)*ratio/2)) = 1;
    mask(end-floor(length(waveIn)*ratio/2)+1: end) = 1;

    specIn = fft(waveIn);
    specOut = specIn .* mask;
    waveOut = ifft(specOut);
end