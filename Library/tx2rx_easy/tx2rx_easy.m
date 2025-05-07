function [packetRx, snr] = tx2rx_easy(packet_1, packet_2, shrink, freq, param)
    % for odd input size and even output size:
    % carrierRx = param.carrierRx - 3*freq;
    % for odd input size and odd output size:
    % NOT Supported!

    sampleRateTx = param.sampleRate;
    sampleRateRx = param.sampleRate / shrink;
    upsample = 4;
    waveAxis = (1: upsample*length(packet_1)) /upsample/sampleRateTx;

    wave_1 = upsampling(packet_1, sampleRateTx, upsample*sampleRateTx);
    wave_2 = upsampling(packet_2, sampleRateTx, upsample*sampleRateTx);
    if param.convert == "up"
        waveRx = wave_1 .* wave_2 .* exp(-1i*2*pi*freq*waveAxis);
    elseif param.carrierTx(1) > param.carrierTx(2)
        waveRx = wave_1 .* conj(wave_2) .* exp(-1i*2*pi*freq*waveAxis);
    elseif param.carrierTx(1) <= param.carrierTx(2)
        waveRx = conj(wave_1) .* wave_2 .* exp(-1i*2*pi*freq*waveAxis);
    end
    waveRx = myFilter(waveRx, sampleRateRx, upsample*sampleRateTx);
    [waveRx, snr] = AddNoise(waveRx, param.powerRF-param.atten, sampleRateTx, param);
    snr = 10*log10(snr);
    packetRx = waveRx(upsample*shrink: upsample*shrink: end);
end

function [signalOut, snr] = AddNoise(signalIn, power, sampleRate, param)
    boltzmann = param.boltzmann;
    temperature = param.temperature;
    noisefigure = param.noisefigure;
    padRate = param.padRate;

    snr = 10^((power-30-noisefigure)/10) / (boltzmann*temperature*sampleRate);
    sigma = GetEnergy(signalIn)/(1+padRate) / snr;
    signalOut = signalIn + randn(1, length(signalIn))*sqrt(sigma/2) + 1i*randn(1, length(signalIn))*sqrt(sigma/2);
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