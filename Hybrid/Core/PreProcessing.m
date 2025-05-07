function [inputNew, weightNew, paramProc] = PreProcessing(inputOrig, weightOrig, shrink, param)
    [inputUnite, weightUnite, paramUnite] = PreUniting(inputOrig, weightOrig, param);
    [inputSlice, weightSlice, paramSlice] = PreSlicing(inputUnite, weightUnite, param);
    [inputPad, weightPad, paramPad] = PrePadding(inputSlice, weightSlice, shrink, param);
    inputNew = inputPad;
    weightNew = weightPad;
    paramProc.paramUnite = paramUnite;
    paramProc.paramSlice = paramSlice;
    paramProc.paramPad = paramPad;
end

