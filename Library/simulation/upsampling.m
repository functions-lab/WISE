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
    waveHigh = ifft(specHigh);
end