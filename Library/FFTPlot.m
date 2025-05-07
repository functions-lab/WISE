function [] = FFTPlot(wave, fs, figureIdx)
    waveLen = length(wave);

    figure(figureIdx);
%     specDouble = abs(fft(wave));
    specDouble = 20*log10(abs(fft(wave))+1e-5);
    if fs > 0
        if mod(waveLen, 2) == 1
            specSingle = specDouble(1: (waveLen+1)/2);
            freqAxis = (0: (waveLen-1)/2)/waveLen*fs;
        else
            specSingle = specDouble(1: waveLen/2);
            freqAxis = (1: waveLen/2)/waveLen*fs;
        end
        plot(freqAxis, specSingle);
    else
        freqAxis = (-waveLen/2: +waveLen/2-1)/waveLen*(-fs);
        plot(freqAxis, fftshift(specDouble));
    end
    xlabel("Frequency (Hz)");
    ylabel("Relative Power (dB)");
    set(gca, 'linewidth', 1.5, 'fontsize', 28, 'fontname', 'Arial');
end