clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

param = GetParam();
param.transMode = "fast";
param.powerRF = -60;

testNum = 100;
batchNum = 1;
inputSizeList = [2 4 8 16 32 64 128 256 512 1024 2048 4096];
outputSizeList = [4 8 16 32 64 128 256 512 1024 2048 4096];

inputSizeNum = length(inputSizeList);
outputSizeNum = length(outputSizeList);

snrMat = NaN(inputSizeNum, outputSizeNum, testNum);
pearMat = NaN(inputSizeNum, outputSizeNum, testNum*batchNum);
rmseMat = NaN(inputSizeNum, outputSizeNum, testNum*batchNum);
for inputSizeIdx = 1: inputSizeNum
    inputSize = inputSizeList(inputSizeIdx);
    for outputSizeIdx = 1: outputSizeNum
        outputSize = outputSizeList(outputSizeIdx);
    
        for testIdx = 1: testNum
            input = randn(batchNum, inputSize) .* exp(1i*2*pi*rand(batchNum, inputSize));
            weight = randn(batchNum, inputSize, outputSize) .* exp(1i*2*pi*rand(batchNum, inputSize, outputSize));
            outputDigit = zeros(batchNum, outputSize);
            for batchIdx = 1: batchNum
                outputDigit(batchIdx, :) = input(batchIdx, :) * reshape(weight(batchIdx, :, :), inputSize, outputSize);
            end

            [outputAnal, snr] = LayerFC(input, weight, "shrink", param);

            snrMat(inputSizeIdx, outputSizeIdx, testIdx) = snr;
            pear = CalcPearson(abs(outputDigit), abs(outputAnal));
            pearMat(inputSizeIdx, outputSizeIdx, (testIdx-1)*batchNum+1: testIdx*batchNum) = pear;
            rmse = CalcRMSE(abs(outputDigit), abs(outputAnal));
            rmseMat(inputSizeIdx, outputSizeIdx, (testIdx-1)*batchNum+1: testIdx*batchNum) = rmse;
        end
        figure(1);
        heatmap(inputSizeList, outputSizeList, mean(snrMat, 3, "omitnan").');
        colormap hot;
        xlabel("Input Size");
        ylabel("Output Size");
        title("SNR (dB)");
    
        figure(2);
        heatmap(inputSizeList, outputSizeList, mean(pearMat, 3, "omitnan").');
        colormap hot;
        xlabel("Input Size");
        ylabel("Output Size");
        title("Pearson");
    
        figure(3);
        heatmap(inputSizeList, outputSizeList, mean(rmseMat, 3, "omitnan").');
        colormap hot;
        xlabel("Input Size");
        ylabel("Output Size");
        title("Rel. RMSE");
    
        save("Result/Result_input_output.mat", ...
            "inputSizeList", "outputSizeList", ...
            "snrMat", "pearMat", "rmseMat");
    end
end
