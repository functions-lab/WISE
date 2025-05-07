function [outputList, waveTime] = LayerConv1D(inputList, kernel, param)
    [batchNum, ~] = size(inputList);
    kernelRepeat = repmat(kernel, batchNum, 1);
    [outputList, waveTime] = ConvCore(inputList, kernelRepeat, param);
end

