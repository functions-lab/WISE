function [outputNewList] = PostUniting(outputUniteList, paramUnite)
%     outputNewList = outputUniteList;
    
    unite = paramUnite.unite;
    batchOrigNum = paramUnite.batchOrigNum;
    outputOrigLen = paramUnite.outputOrigLen;

    outputNewList = zeros(batchOrigNum, outputOrigLen);
    for uniteIdx = 1: unite
        if uniteIdx <= mod(batchOrigNum, unite)
            span = ceil(batchOrigNum/unite);
        else
            span = floor(batchOrigNum/unite);
        end
        outputPtr = (uniteIdx-1) * outputOrigLen;
        outputNewList((0: span-1)*unite+uniteIdx, :) = ...
            outputUniteList(1: span, outputPtr+1: outputPtr+outputOrigLen);
    end
end

