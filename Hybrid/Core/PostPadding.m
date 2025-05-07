function [outputNewList] = PostPadding(outputPadList, paramPad)
    indexOutput = paramPad.indexOutput;
%     outputSlice = outputPad(:, guardOutputLen+1: guardOutputLen+outputSliceLen);
    outputNewList = outputPadList(:, indexOutput);
end

