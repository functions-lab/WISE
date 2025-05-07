function [outputList] = LayerFCCore_full(inputList, weightList, freqOffset, param)
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
    [waveOutput, SNR, CFO] = Tx2Rx_gnu(waveInput, waveWeight, param.sampleRate, 1, 0, param);
    disp("Transmission Summary:");
    disp("SNR: "+SNR+"dB");
    disp("CFO: "+CFO+"Hz");

    outputList = LayerFC_analyzeRx_full(waveOutput, freqOffset, shape, param);
end