function [outputNewList] = PostSlicing(outputSliceList, paramSlice)
    slice = paramSlice.slice;
    batchOrigNum = paramSlice.batchOrigNum;
    outputOrigLen = paramSlice.outputOrigLen;

    outputNewList = zeros(batchOrigNum, outputOrigLen);
    endIdx = 0;
    for sliceIdx = 1: slice
        if sliceIdx <= mod(outputOrigLen, slice)
            span = ceil(outputOrigLen/slice);
        else
            span = floor(outputOrigLen/slice);
        end
        startIdx = endIdx + 1;
        endIdx = endIdx + span;
        outputNewList(:, startIdx: endIdx) = ...
            outputSliceList((0: batchOrigNum-1)*slice+sliceIdx, 1: span);
    end
end

