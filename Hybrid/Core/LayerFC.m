function [outputMat, SNR, waveTime] = LayerFC(input, weight, method, param)
    if ndims(input) == 3
        disp("Multiple User Found!");
        [userNum, testNum, inputLen] = size(input);
        inputList = input;
        if userNum ~= param.userNum
            disp("Warning: User Number NOT Matched!");
        end
    elseif ndims(input) == 2
        disp("Single User Found and Duplicated!");
        [testNum, inputLen] = size(input);
        inputList = repmat(reshape(input, [1 testNum inputLen]), [param.userNum 1 1]);
    end
    if ndims(weight) == 3
        disp("Multiple Weight Matrices Found!");
        outputLen = size(weight, 3);
        weightList = weight;
        repeatNum = 1;
    elseif(size(weight, 1)==testNum)&&(size(weight, 2)==inputLen)
        disp("Vector Inner Product Found!");
        outputLen = 1;
        weightList = weight;
        repeatNum = 1;
    else
        disp("Single Weight Matrix Found and Duplicated!");
        outputLen = size(weight, 2);
        weightList = repmat(reshape(weight, [1 inputLen outputLen]), testNum, 1, 1);
        repeatNum = testNum;
    end
    transMode = param.transMode;
    autoEdge = param.autoEdge;
    sampleRate = param.sampleRate;
    attenList = param.attenList;
    userNum = param.userNum;
    
    shrink = -1;
    if contains(method, "down-")
        methodChar = char(method);
        shrink = round(str2double(methodChar(6: end)));
    elseif(method == "auto")&&(transMode=="exp")&&(inputLen>autoEdge)
        shrink = autoEdge;
    end

    [inputNew, weightNew, paramProc] = PreProcessing(inputList, weightList, shrink, param);
    subOffset = paramProc.paramPad.subOffset;

    [batchNewNum, inputNewLen, outputNewLen] = size(weightNew);
    shape.symNum = batchNewNum;
    shape.inputLen = inputNewLen;
    shape.outputLen = outputNewLen;

    [waveInput, waveWeight, waveLen] = LayerFC_generateTx(inputNew, weightNew, repeatNum, subOffset, shape, param);
%     TxOnly_mult(waveInput, waveWeight, param);
    if mod(inputNewLen, 2) == 1
        subOffset = subOffset - floor(outputNewLen/2);
    end
    waveTime = waveLen/sampleRate;

    snrList = NaN(length(attenList), userNum);
    outputMat = NaN(length(attenList), userNum, testNum, outputLen);
    for attenIdx = 1: length(attenList)
        disp(attenIdx+"/"+length(attenList));
        atten = attenList(attenIdx);
        waveInputAtten = waveInput / sqrt(10^(atten/10));
        param.atten = atten;

        if method == "full"
            freqOffset = (2*subOffset-round(outputNewLen/2)) / inputNewLen/outputNewLen;
            [waveOutput, SNR, CFO] = Tx2Rx_all(waveInputAtten, waveWeight, 1, freqOffset, param);
            
            outputList = NaN(userNum, testNum, outputLen);
            for userIdx = 1: userNum
                outputNew = LayerFC_analyzeRx_full(waveOutput, subOffset, shape, param);
                outputList(userIdx, :, :) = PostProcessing(outputNew, paramProc);
            end
        else
            if shrink < 0
                shrink = inputNewLen;
            end
            freqOffset = (2*subOffset-round(outputNewLen/2)) / inputNewLen/outputNewLen;
            [waveOutput, SNR, CFO] = Tx2Rx_all(waveInputAtten, waveWeight, shrink, freqOffset, param);

            outputList = NaN(userNum, testNum, outputLen);
            for userIdx = 1: userNum
                outputNew = LayerFC_analyzeRx(waveOutput(userIdx, :), round(inputNewLen/shrink), shape, param);
                outputList(userIdx, :, :) = PostProcessing(outputNew, paramProc);
            end
        end
        disp("Transmission Summary:");
        disp("SNR: "+mean(SNR)+"dB");
        disp("CFO: "+mean(CFO)+"Hz");

        outputMat(attenIdx, :, :, :) = outputList;
        snrList(attenIdx, :) = SNR;
    end
%     outputMat = squeeze(outputMat);
end