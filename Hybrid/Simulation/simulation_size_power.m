clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

param = GetParam();
param.transMode = "fast";

testNum = 100;
inputSizeList = [2 4 8 16 32 64 128 256 512 1024 2048 4096];
outputSizeList = [2 4 8 16 32 64 128 256 512 1024 2048 4096];
powerList = [-50, -55, -60, -65, -70, -75, -80, -85, -90, -95, -100, -105, -110];

dimenNum = min(length(inputSizeList), length(outputSizeList));
powerNum = length(powerList);

snrMat = NaN(dimenNum, powerNum, testNum);
pearMat = NaN(dimenNum, powerNum, testNum);
rmseMat = NaN(dimenNum, powerNum, testNum);
for dimenIdx = 1: dimenNum
    inputSize = inputSizeList(dimenIdx);
    outputSize = outputSizeList(dimenIdx);

    for testIdx = 1: testNum
        input = randn(1, inputSize) .* exp(1i*2*pi*rand(1, inputSize));
        weight = randn(1, inputSize, outputSize) .* exp(1i*2*pi*rand(1, inputSize, outputSize));
        outputDigit = input * reshape(weight, inputSize, outputSize);

        for powerIdx = 1: powerNum
            param.powerRF = powerList(powerIdx);

            [outputAnal, snr] = LayerFC(input, weight, "shrink", param);

            snrMat(dimenIdx, powerIdx, testIdx) = snr;
            pear = CalcPearson(abs(outputDigit), abs(outputAnal));
            pearMat(dimenIdx, powerIdx, testIdx) = pear;
            rmse = CalcRMSE(abs(outputDigit), abs(outputAnal));
            rmseMat(dimenIdx, powerIdx, testIdx) = rmse;
        end
    end
    figure(1);
    heatmap(inputSizeList, powerList, mean(snrMat, 3, "omitnan").');
    colormap hot;
    xlabel("Input/Output Size");
    ylabel("RF Power");
    title("SNR (dB)");

    figure(2);
    heatmap(inputSizeList, powerList, mean(pearMat, 3, "omitnan").');
    colormap hot;
    xlabel("Input/Output Size");
    ylabel("RF Power");
    title("Pearson");

    figure(3);
    heatmap(inputSizeList, powerList, mean(rmseMat, 3, "omitnan").');
    colormap hot;
    xlabel("Input/Output Size");
    ylabel("RF Power");
    title("Rel. RMSE");

    save("Result/Result_size_power.mat", ...
        "inputSizeList", "outputSizeList", "powerList", ...
        "snrMat", "pearMat", "rmseMat");
end
