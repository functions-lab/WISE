function [gain] = Power2Gain(power)
    gain = 10.*log10(power+1e-10);
end
