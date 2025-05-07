function [inputSliceList, weightSliceList, paramSlice] = PreSlicing(inputOrigList, weightOrigList, param)
    subMax = param.subMax;
    decMode = param.decMode;
    userNum = param.userNum;
    [batchOrigNum, inputLen, outputOrigLen] = size(weightOrigList);

    if decMode == "inner"
        slice = outputOrigLen;
    elseif contains(decMode, "split-")
        decModeChar = char(decMode);
        split = round(str2double(decModeChar(7: end)));
        slice = ceil(outputOrigLen/split);
    else
        if inputLen > subMax
            slice = outputOrigLen;
        else
            slice = max(ceil(outputOrigLen/floor(subMax/inputLen)), 1);
        end
    end

    batchSliceNum = batchOrigNum * slice;
    outputSliceLen = ceil(outputOrigLen / slice);
    if slice > 1
        inputSliceList = zeros(userNum, batchSliceNum, inputLen);
        weightSliceList = zeros(batchSliceNum, inputLen, outputSliceLen);
        endIdx = 0;
        for sliceIdx = 1: slice
            if sliceIdx <= mod(outputOrigLen, slice)
                span = ceil(outputOrigLen/slice);
            else
                span = floor(outputOrigLen/slice);
            end
            startIdx = endIdx + 1;
            endIdx = endIdx + span;
            inputSliceList(:, (0: batchOrigNum-1)*slice+sliceIdx, :) = inputOrigList;
            weightSliceList((0: batchOrigNum-1)*slice+sliceIdx, :, 1: span) = ...
                weightOrigList(:, :, startIdx: endIdx);
        end
    else
        inputSliceList = inputOrigList;
        weightSliceList = weightOrigList;
    end

    paramSlice.slice = slice;
    paramSlice.batchOrigNum = batchOrigNum;
    paramSlice.batchSliceNum = batchSliceNum;
    paramSlice.inputLen = inputLen;
    paramSlice.outputOrigLen = outputOrigLen;
    paramSlice.outputSliceLen = outputSliceLen;
end