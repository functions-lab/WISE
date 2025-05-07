function [outputList] = LayerFCCore_shrink(inputList, weightList, freqOffset, param)
    [symNum_1, inputLen_1] = size(inputList);
    [symNum_2, inputLen_2, outputLen] = size(weightList);
    if symNum_1 ~= symNum_2
        disp("Warning: Input Symbol Number NOT Matched!");
    end
    symNum = min(symNum_1, symNum_2);
    if inputLen_1 ~= inputLen_2
        disp("Warning: InputSize NOT Matched!");
    end
    inputLen = min(inputLen_1, inputLen_2);

    shape.symNum = symNum;
    shape.inputLen = inputLen;
    shape.outputLen = outputLen;

    [waveInput, waveWeight] = LayerFC_generateTx(inputList, weightList, freqOffset, shape, param);

%     waveOutput = waveInput .* waveWeight;
    shrink = inputLen;
    freq = (2*freqOffset-1) * param.sampleRate/inputLen/outputLen;
    waveOutput = Tx2Rx_gnu(waveInput, waveWeight, param.sampleRate, shrink, freq, param);

    outputList = LayerFC_analyzeRx_shrink(waveOutput, shape, param);
end