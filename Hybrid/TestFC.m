clear;
clc;
close all;
addpath(genpath("../Library"));
addpath(genpath("./Core"));
rng(0);

%%

param = GetParam_low();
param.transMode = "easy";
userNum = 1;
param.userNum = userNum;

% param.padRate = 0;

testNum = 20;
inputSize = 100; % 4096
outputSize = 100; % 4096
input = rand(testNum, inputSize) .* exp(1i*2*pi*rand(testNum, inputSize));
weight = rand(testNum, inputSize, outputSize) .* exp(1i*2*pi*rand(testNum, inputSize, outputSize));

outputDigitList = zeros(testNum, outputSize);
for testIdx = 1: testNum
    outputDigitList(testIdx, :) = input(testIdx, :) * reshape(weight(testIdx, :, :), [inputSize outputSize]);
end

%%

outputAnalListAll = LayerFC(input, weight, "auto", param);

for userIdx = 1: userNum
    outputAnalList = squeeze(outputAnalListAll(1, userIdx, :, :));
    pearson = CalcPearson(abs(outputDigitList), abs(outputAnalList));
    rmse = CalcRMSE(abs(outputDigitList), abs(outputAnalList));

    figure;
    scatter(abs(outputDigitList), abs(outputAnalList));
    title("RMSE: "+mean(rmse)+" Pear: "+mean(pearson));
    xlabel("Digital Computing");
    ylabel("Analog Computing");
    
    figure;
    plot(angle(outputDigitList./outputAnalList).');
end
