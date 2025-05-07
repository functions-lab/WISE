function [waveOutput, SNR, CFO] = Tx2Rx_all(waveInput, waveWeight, shrink, freqOffset, param)
    sampleRate = param.sampleRate;
    transMode = param.transMode;
    userNum = param.userNum;

    if transMode == "exp"
        if size(waveInput, 1) == 1
            waveInputTemp = repmat(waveInput, [userNum 1]);
        else
            waveInputTemp = waveInput;
        end
        [waveOutput, SNR, CFO] = Tx2Rx_mult( ...
            waveInputTemp, waveWeight, userNum, sampleRate, shrink, freqOffset*sampleRate, param);
    elseif transMode == "easy"
        if size(waveInput, 1) == 1
            [waveOutputTemp, SNR] = tx2rx_easy(waveInput, waveWeight, shrink, freqOffset*sampleRate, param);
            waveOutput = repmat(waveOutputTemp, [userNum 1]);
        else
            waveOutput = NaN(userNum, round(length(waveInput)/shrink));
            for userIdx = 1: userNum
                [waveOutputTemp, SNR] = tx2rx_easy(waveInput, waveWeight, shrink, freqOffset*sampleRate, param);
            end
            waveOutput(userIdx, :) = waveOutputTemp;
        end
        CFO = 0;
%     elseif transMode == "fast"
%         [waveOutput, SNR] = tx2rx_fast(waveInput, waveWeight, shrink, freqOffset*sampleRate, param);
%         CFO = 0;
%     elseif transMode == "link"
%         [waveOutput, SNR] = tx2rx_link(waveInput, waveWeight, sampleRate, shrink, freqOffset*sampleRate, param);
%         CFO = 0;
%     elseif transMode == "sim"
%         [waveOutput, SNR] = Tx2Rx_sim(waveInput, waveWeight, shrink, freqOffset*sampleRate, param);
%         CFO = 0;
    else
        disp("Warning: Transmission Mode NOT Found!");
    end
end

