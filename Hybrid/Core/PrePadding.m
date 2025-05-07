function [inputPadList, weightPadList, paramPad] = PrePadding(inputOrigList, weightOrigList, shrink, param)
    guardDC = param.guardDC;
    guardInput = param.guardInput;
    guardOutput = param.guardOutput;

    userNum = param.userNum;
    [batchNum, inputOrigLen, outputOrigLen] = size(weightOrigList);

    guardDCLen = ceil(inputOrigLen * guardDC);
    middle = ceil(inputOrigLen/2);
    if shrink > 0
        guardInputLen = ceil(inputOrigLen * guardInput);
        inputTempLen = inputOrigLen + 6 * guardDCLen + 2 * guardInputLen;
        inputPadLen = ceil(inputTempLen/shrink) * shrink;
        inputDeltaLen = round((inputPadLen - inputTempLen)/2); 
        indexLeft = guardDCLen+guardInputLen+inputDeltaLen+1: guardDCLen+guardInputLen+inputDeltaLen+middle;
        indexRight = guardDCLen*5+guardInputLen+inputDeltaLen+middle+1: guardDCLen*5+guardInputLen+inputDeltaLen+inputOrigLen;
    else
        guardInputLen = ceil(inputOrigLen * guardInput);
        inputPadLen = inputOrigLen + 6 * guardDCLen + 2 * guardInputLen;
        indexLeft = guardDCLen+guardInputLen+1: guardDCLen+guardInputLen+middle;
        indexRight = guardDCLen*5+guardInputLen+middle+1: guardDCLen*5+guardInputLen+inputOrigLen;
    end

    guardOutputLen = ceil(outputOrigLen * guardOutput);
    outputPadLen = outputOrigLen + 2 * guardOutputLen;
    indexOutput = guardOutputLen+1: guardOutputLen+outputOrigLen;

    inputPadList = zeros(userNum, batchNum, inputPadLen);
    inputPadList(:, :, indexLeft) = inputOrigList(:, :, 1: middle);
    inputPadList(:, :, indexRight) = inputOrigList(:, :, middle+1: end);
    weightPadList = zeros(batchNum, inputPadLen, outputPadLen);
    weightPadList(:, indexLeft, indexOutput) = weightOrigList(:, 1: middle, :);
    weightPadList(:, indexRight, indexOutput) = weightOrigList(:, middle+1: end, :);

    paramPad.indexLeft = indexLeft;
    paramPad.indexRight = indexRight;
    paramPad.indexOutput = indexOutput;
    paramPad.subOffset = guardDCLen*outputPadLen;
end

