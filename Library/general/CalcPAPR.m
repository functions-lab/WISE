function [papr, waveAvg, waveMax] = CalcPAPR(wave)
    waveAvg = sqrt(mean(abs(wave).^2));
    waveMax = max(abs(wave));
    papr = 20*log10(waveMax/waveAvg);
end

