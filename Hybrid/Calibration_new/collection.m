clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

testNum = 10000;
inputSizeList = [300];
outputSize = 10;
token = "corner3";

param = GetParam_low();
param.gainTx = [14 30];
param.encMode = "freq"; % Different!!!
param.decMode = "freq"; % "split-1";
% param.delay = 0.85;

param.guardInput = 0;
param.guardOutput = 0;
param.guardDC = 0;

for inputSize = inputSizeList
    fileIn = "dataset/dataIn_"+inputSize+"_"+outputSize+".mat";
    fileOut = "dataset/dataOut_"+inputSize+"_"+outputSize+"_"+token+".mat";
%     if exist(fileIn, 'file')&&exist(fileOut, 'file')
%         continue;
%     end

    inputAll = rand(testNum, inputSize) .* exp(1i*2*pi*rand(testNum, inputSize)) *sqrt(inputSize)*outputSize*5/9;
    weightAll = rand(testNum, inputSize, outputSize) .* exp(1i*2*pi*rand(testNum, inputSize, outputSize)) *sqrt(inputSize*outputSize)*5/9;
    save(fileIn, "inputAll", "weightAll", "-v7.3");

    outputDigitAll = NaN(testNum, outputSize);
    for testIdx = 1: testNum
        outputDigitAll(testIdx, :) = inputAll(testIdx, :) * reshape(weightAll(testIdx, :, :), inputSize, outputSize);
    end
    outputAnalAll = LayerFC(inputAll, weightAll, "auto", param);
    outputAnalAll = squeeze(outputAnalAll);

    outputDigit = abs(reshape(outputDigitAll, 1, []));
    outputAnal = abs(reshape(outputAnalAll, 1, []));
    pearson = CalcPearson(abs(outputDigit), abs(outputAnal));
    rmse = CalcRMSE(abs(outputDigit), abs(outputAnal));

    figure(1);
    hold on;
    for outputIdx = 1: outputSize
        scatter(abs(outputDigitAll(:, outputIdx)), abs(outputAnalAll(:, outputIdx)));
    end
    hold off;
    title("RMSE: "+rmse+" Pear: "+pearson);
    xlabel("Digital Computing");
    ylabel("Analog Computing");

    save(fileOut, "outputDigitAll", "outputAnalAll");
end