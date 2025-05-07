function [outputList] = LayerFC_conv(inputList, weight, param)
    transient = param.transient;

    [batchNum, inputLen_1] = size(inputList);
    [inputLen_2, outputLen] = size(weight);
    if inputLen_1 ~= inputLen_2
        disp("Warning: InputSize NOT Matched!");
    end
    inputLen = min(inputLen_1, inputLen_2);
    outputPadLen = round(outputLen * transient);
    outputAllLen = outputLen + 2 * outputPadLen;

    mapping = zeros(inputLen, inputLen*outputAllLen);
    for inputIdx = 1: inputLen
        mapping(inputIdx, (inputIdx-1)*outputAllLen+1) = 1;
    end
    inputConv = inputList * mapping;
    
    weightAll = zeros(inputLen, outputAllLen);
    weightAll(:, outputPadLen+1: outputPadLen+outputLen) = weight;
    weightConv = repmat(flip(reshape(weightAll.', 1, [])), batchNum, 1);

    outputConv = ConvCore(inputConv, weightConv, param);

    outputAllList = fliplr(outputConv(:, inputLen*outputAllLen-outputAllLen+1: inputLen*outputAllLen));
    outputList = outputAllList(:, outputPadLen+1: outputPadLen+outputLen);
end

