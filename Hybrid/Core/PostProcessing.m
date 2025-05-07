function [outputNew] = PostProcessing(outputOrig, paramProc)
    paramPad = paramProc.paramPad;
    paramSlice = paramProc.paramSlice;
    paramUnite = paramProc.paramUnite;
    outputPad = outputOrig;

    outputSlice = PostPadding(outputPad, paramPad);
    outputUnite = PostSlicing(outputSlice, paramSlice);
    outputNew = PostUniting(outputUnite, paramUnite);
end

