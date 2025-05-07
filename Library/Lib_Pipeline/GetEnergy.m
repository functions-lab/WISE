function [energy] = GetEnergy(wave)
    waveCal = wave; % - mean(wave);
    energy = mean(abs(waveCal).^2);
end