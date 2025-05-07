function [inputUniteList, weightUniteList, paramUnite] = PreUniting(inputOrigList, weightOrigList, param)
%     inputUniteList = inputOrigList;
%     weightUniteList = weightOrigList;
%     paramUnite = {};

    subMin = param.subMin;
    userNum = param.userNum;
    [batchOrigNum, inputOrigLen, outputOrigLen] = size(weightOrigList);
    unite = ceil(sqrt(subMin/inputOrigLen/outputOrigLen));

    batchUniteNum = ceil(batchOrigNum/unite);
    inputUniteLen = inputOrigLen * unite;
    outputUniteLen = outputOrigLen * unite;
    if unite > 1
        inputUniteList = zeros(userNum, batchUniteNum, inputUniteLen);
        weightUniteList = zeros(batchUniteNum, inputUniteLen, outputUniteLen);
        randPos = randperm(unite);
        for uniteIdx = 1: unite
            if uniteIdx <= mod(batchOrigNum, unite)
                span = ceil(batchOrigNum/unite);
            else
                span = floor(batchOrigNum/unite);
            end
            inputPtr = (randPos(uniteIdx)-1) * inputOrigLen;
            outputPtr = (uniteIdx-1) * outputOrigLen;
            inputUniteList(:, 1: span, inputPtr+1: inputPtr+inputOrigLen) = ...
                inputOrigList(:, (0: span-1)*unite+uniteIdx, :) * sqrt(unite);
            weightUniteList(1: span, inputPtr+1: inputPtr+inputOrigLen, outputPtr+1: outputPtr+outputOrigLen) = ...
                weightOrigList((0: span-1)*unite+uniteIdx, :, :) * sqrt(unite);
        end
    else
        inputUniteList = inputOrigList;
        weightUniteList = weightOrigList;
    end

    paramUnite.unite = unite;
    paramUnite.batchOrigNum = batchOrigNum;
    paramUnite.batchUniteNum = batchUniteNum;
    paramUnite.inputOrigLen = inputOrigLen;
    paramUnite.inputUniteLen = inputUniteLen;
    paramUnite.outputOrigLen = outputOrigLen;
    paramUnite.outputUniteLen = outputUniteLen;
end