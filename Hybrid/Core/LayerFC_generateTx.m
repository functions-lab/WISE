function [waveInput, waveWeight, waveLen] = LayerFC_generateTx(inputList, weightList, repeatNum, subOffset, shape, param)
    symNum = shape.symNum;
    inputLen = shape.inputLen;
    outputLen = shape.outputLen;
    
    encMode = param.encMode;
    decMode = param.decMode;
    convert = param.convert;
    carrierTx = param.carrierTx;
    userNum = param.userNum;
    delay = param.delay;
    calib = param.calib;
    precode = param.precode;
    if param.cpRate >= 0
        cpRate = param.cpRate;
    else
        cpRate = 2/outputLen; % Only include the first lobe of sinc function
    end
    padRate = param.padRate;

    cpLen = inputLen*round(outputLen*cpRate);
    padLen = inputLen*round(outputLen*padRate);
    batchLen = inputLen * outputLen + cpLen + padLen;
    inputNorm = param.inputNorm * sqrt((batchLen-padLen)/batchLen);
    weightNorm = param.weightNorm * sqrt((batchLen-padLen)/batchLen);
    waveLen = symNum * (inputLen * outputLen + cpLen);

    % Encode Input Waveform
    if precode == "input"
        csiInput = conj(CalcCSI(inputLen, calib, delay));
        if(size(csiInput, 1) ~= userNum)
            disp("Warning: CSI Cache Number NOT Match User Number!");
        end
    else
        csiInput = ones(userNum, inputLen);
    end
    waveInput = zeros(userNum, symNum*batchLen);
    for symIdx = 1: symNum
        input = reshape(inputList(:, symIdx, :), userNum, []);
        startIdx = (symIdx-1) * batchLen + 1;
        endIdx = symIdx * batchLen;
        if encMode == "time"
            if precode == "input"
                waveSing = [];
                for userIdx = 1: userNum
                    inputFreq = fft(input(userIdx, :));
                    inputFreq = circshift(inputFreq, -round(subOffset/outputLen)+ceil(inputLen/2));
                    waveSingTemp = EncodeWave(inputFreq, round(subOffset/outputLen)-ceil(inputLen/2), csiInput(userIdx, :)) / outputLen;
                    waveSing = [waveSing; waveSingTemp]; %#ok<AGROW> 
                end
            else
                waveSing = input;
            end
            if symIdx <= round(symNum/repeatNum)
                freqOffset = round(subOffset/outputLen)-ceil(inputLen/2);
                transEnc = EncodeWaveTrans(inputLen, freqOffset) / outputLen;
                weightOne = reshape(weightList(symIdx, :, :), [inputLen outputLen]);
                weightList(symIdx, :, :) = transEnc * weightOne;

%                 weightOne = reshape(weightList(symIdx, :, :), [inputLen outputLen]) / inputLen/outputLen;
%                 for inputIdx = 1: inputLen
%                     row = mod(inputIdx - freqOffset + 1, inputLen);
%                     transEnc = exp(2*pi*1i/inputLen.*((0: inputLen-1) * row));
%                     weightList(symIdx, inputIdx, :) = transEnc * weightOne;
%                 end
            end
        else
            waveSing = [];
            for userIdx = 1: userNum
                waveSingTemp = EncodeWave(input(userIdx, :), round(subOffset/outputLen)-ceil(inputLen/2), csiInput(userIdx, :)) / outputLen;
                waveSing = [waveSing; waveSingTemp]; %#ok<AGROW> 
            end
        end
        if decMode == "time"
            if symIdx <= round(symNum/repeatNum)
                weightOne = reshape(weightList(symIdx, :, :), [inputLen outputLen]);
                transDec = DecodeWaveTrans(outputLen);
                weightList(symIdx, :, :) = weightOne * transDec;
            end
        end
        if inputNorm < 0
            wavePower = sqrt(mean(abs(waveSing).^2, 2));
            for userIdx = 1: userNum
                waveSing(userIdx, :) = -inputNorm * waveSing(userIdx, :) ./ wavePower(userIdx);
            end
        end
        waveMult = repmat(waveSing, 1, outputLen);
        waveCP = AddCP(waveMult, cpLen, padLen);
        waveInput(:, startIdx: endIdx) = waveCP;
    end
    if inputNorm > 0
        wavePower = sqrt(mean(abs(waveInput).^2, 2));
        for userIdx = 1: userNum
            waveInput(userIdx, :) = inputNorm * waveInput(userIdx, :) ./ wavePower(userIdx);
        end
    end
    
    % Encode Weight Waveform
    if precode == "weight"
        csiWeight = mean(CalcCSI(inputLen*outputLen, calib, delay), 1);
    else
        csiWeight = ones(1, inputLen*outputLen);
    end
    weightConv = flip(reshape(permute(weightList, [1 3 2]), symNum, []), 2);
    waveWeight = zeros(1, round(symNum/repeatNum)*batchLen);
    for symIdx = 1: round(symNum/repeatNum)
        startIdx = (symIdx-1) * batchLen + 1;
        endIdx = symIdx * batchLen;
        waveSing = EncodeWave(weightConv(symIdx, :), subOffset-ceil(inputLen/2)*outputLen, csiWeight);
        if weightNorm < 0
            waveSing = -weightNorm * waveSing ./ sqrt(mean(abs(waveSing).^2));
        end
        waveCP = AddCP(waveSing, cpLen, padLen);
        waveWeight(startIdx: endIdx) = waveCP;
    end
    if weightNorm > 0
        waveWeight = weightNorm * waveWeight ./ sqrt(mean(abs(waveWeight).^2));
    end
    waveWeight = repmat(waveWeight, [1 repeatNum]);

    if convert == "down"
        if carrierTx(1) > carrierTx(2)
            waveWeight = conj(waveWeight);
        else
            waveInput = conj(waveInput);
        end
    end
    % Do Nothing with NaN inputNorm/weightNorm
end

function [transform] = EncodeWaveTrans(fftSize, freqOffset)
    transform = circshift(conj(dftmtx(fftSize))/fftSize, -freqOffset, 1);
%     wave = input * transform;
end

function [transform] = DecodeWaveTrans(fftSize)
    transform = circshift(dftmtx(fftSize), ceil(fftSize/2), 2);
%     fftSize= length(wave);
%     transform = circshift(dftmtx(fftSize), ceil(fftSize/2), 2);
%     output = wave * transform;
end

function [wave] = EncodeWave(input, freqOffset, csi)
    spec = circshift(input./csi, freqOffset);
    wave = ifft(spec);
end

function [waveOut] = AddCP(waveIn, cpLen, padLen)
    if cpLen == 0 % for acceleration
        waveCP = waveIn;
    else
        waveMult = repmat(waveIn, 1, ceil(cpLen/length(waveIn)/2));
        waveCP = [waveMult(:, end-round(cpLen/2)+1: end) waveIn waveMult(:, 1: cpLen - round(cpLen/2))];
    end
    if padLen == 0
        waveOut = waveCP;
    else
        padLeft = floor(padLen/2);
        padRight = padLen - padLeft;
        waveOut = [zeros(size(waveIn, 1), padLeft) waveCP zeros(size(waveIn, 1), padRight)];
    end
end

function [csi, slope] = CalcCSI(subNum, calib, delay)
    if ~isempty(calib)
        csi = NaN(length(calib), subNum);
        for calibIdx = 1: length(calib)
            if ~exist(calib(calibIdx), "file")
                disp("Warning: CSI Cache File NOT Found!");
                continue;
            end
            respOrig = double(load(calib(calibIdx)).resp);
            respNorm = respOrig / sqrt(mean(abs(respOrig).^2));
            respNew = interpolate(respNorm, subNum, length(respOrig));
            slope = load(calib(calibIdx)).slope;
            phase = (1: subNum)/subNum * slope;
            csi(calibIdx, :) = respNew .* exp(-1i*phase);
        end
    elseif delay ~= 0
        phase = (1: subNum)/subNum * delay;
        csi = exp(-1i*2*pi*phase);
    else
        csi = ones(1, subNum);
    end
end

function [output] = interpolate(input, outputLen, inputLen)
    inputAxis = ((1: inputLen)-0.5)/inputLen;
    outputAxis = ((1: outputLen)-0.5)/outputLen;

    output = NaN(1, outputLen);
    inputIdx = 1;
    for outputIdx = 1: outputLen
        while(inputIdx < inputLen)&& ...
                (abs(inputAxis(inputIdx+1)-outputAxis(outputIdx))<abs(inputAxis(inputIdx)-outputAxis(outputIdx)))
            inputIdx = inputIdx + 1;
        end
        output(outputIdx) = input(inputIdx);
    end
end