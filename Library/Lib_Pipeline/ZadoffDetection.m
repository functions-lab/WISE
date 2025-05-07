function [offsetList, corrList] = ZadoffDetection(wave, winLen, deltaLen, threshold)
    waveLen = length(wave);
    neighbor = 10;

    corrAll = zeros(1, waveLen-deltaLen-winLen+1);

    zadoff_1 = wave(1: winLen);
    zadoff_2 = wave(deltaLen+1: deltaLen+winLen);
    product = sum(zadoff_1 .* conj(zadoff_2));
    sum_1 = sum(zadoff_1);
    sum_2 = sum(zadoff_2);
    energy_1 = sum(abs(zadoff_1).^2);
    energy_2 = sum(abs(zadoff_2).^2);
    corrAll(1) = abs(product-sum_1*conj(sum_2)/winLen) / sqrt((energy_1-sum_1*conj(sum_1)/winLen)*(energy_2-sum_2*conj(sum_2)/winLen));
    for offset = 1: waveLen-deltaLen-winLen
        iqIn_1 = wave(offset+winLen);
        iqIn_2 = wave(offset+deltaLen+winLen);
        iqOut_1 = wave(offset);
        iqOut_2 = wave(offset+deltaLen);

        sum_1 = sum_1 - iqOut_1 + iqIn_1;
        sum_2 = sum_2 - iqOut_2 + iqIn_2;
        product = product - iqOut_1*conj(iqOut_2) + iqIn_1*conj(iqIn_2);
        energy_1 = energy_1 - abs(iqOut_1)^2 + abs(iqIn_1).^2;
        energy_2 = energy_2 - abs(iqOut_2)^2 + abs(iqIn_2).^2;
        corr = abs(product-sum_1*conj(sum_2)/winLen) / sqrt((energy_1-sum_1*conj(sum_1)/winLen)*(energy_2-sum_2*conj(sum_2)/winLen));
        corrAll(offset+1) = corr;
    end

    offsetList = [];
    corrList = [];
    for offset = neighbor+1: waveLen-deltaLen-winLen+1-neighbor
        corr = corrAll(offset);
        if corr > threshold
            if corr < max(corrAll(offset-neighbor: offset-1))
                continue;
            end
            if corr < max(corrAll(offset+1: offset+neighbor))
                continue;
            end
            offsetList = [offsetList offset]; %#ok<AGROW> 
            corrList = [corrList corr]; %#ok<AGROW> 
        end
    end
%     for offset = 0: waveLen-deltaLen-winLen
%         corr = corrAll(offset+1);
%         if corr > threshold
%             if (offset>=1)&&(corr<corrAll(offset))
%                 continue;
%             end
%             if (offset+2<=waveLen-deltaLen-winLen+1)&&(corr<corrAll(offset+2))
%                 continue;
%             end
%             offsetList = [offsetList offset]; %#ok<AGROW> 
%             corrList = [corrList corr]; %#ok<AGROW> 
%         end
%     end
end

% corrAll = zeros(1, waveLen-deltaLen-winLen+1);
% 
% zadoff_1 = wave(1: winLen);
% zadoff_2 = wave(deltaLen+1: deltaLen+winLen);
% product = sum(zadoff_1 .* conj(zadoff_2));
% energy_1 = sum(abs(zadoff_1).^2);
% energy_2 = sum(abs(zadoff_2).^2);
% corrAll(1) = abs(product) / sqrt(energy_1*energy_2);
% for offset = 1: waveLen-deltaLen-winLen
%     iqIn_1 = wave(offset+winLen);
%     iqIn_2 = wave(offset+deltaLen+winLen);
%     iqOut_1 = wave(offset);
%     iqOut_2 = wave(offset+deltaLen);
% 
%     product = product - iqOut_1*conj(iqOut_2) + iqIn_1*conj(iqIn_2);
%     energy_1 = energy_1 - abs(iqOut_1)^2 + abs(iqIn_1).^2;
%     energy_2 = energy_2 - abs(iqOut_2)^2 + abs(iqIn_2).^2;
%     corr = abs(product) / sqrt(energy_1*energy_2);
%     corrAll(offset+1) = corr;
% end