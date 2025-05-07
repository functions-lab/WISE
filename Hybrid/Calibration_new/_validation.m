clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

testNum = 10000;
batchNum = 10000;
inputSizeList = [100]; % [100 300 784 1000 4000];
outputSize = 6;

ratio = 0.9;

pearMat = NaN(1, length(inputSizeList));
rmseMat = NaN(1, length(inputSizeList));
for inputSizeIdx = 1: length(inputSizeList)
    inputSize = inputSizeList(inputSizeIdx);

    fileIn = "dataset/dataIn_"+inputSize+"_"+outputSize+".mat";
    fileOut = "dataset/dataOut_"+inputSize+"_"+outputSize+".mat";
    if ~exist(fileIn, 'file')||~exist(fileOut, 'file')
        continue;
    end


    scalar = 0.5*inputSize*inputSize*outputSize;
    inputAll = load("dataset/dataIn_"+inputSize+"_"+outputSize+".mat").inputAll;
    weightAll = load("dataset/dataIn_"+inputSize+"_"+outputSize+".mat").weightAll;
    outputAnalAll = abs(load("dataset/dataOut_"+inputSize+"_"+outputSize+".mat").outputAnalAll);
    
    cacheName = "./Result/result_"+inputSize+"_"+outputSize+"_one/result.mat";
    if exist(cacheName, 'file')
        alphaMat = load(cacheName).alphaMat;
        betaMat = load(cacheName).betaMat;
        gammaMat = load(cacheName).gammaMat;
        deltaMat = load(cacheName).deltaMat;
    else
        alpha = 1; % mean(abs(outputDigitAll), "all") / mean(abs(outputAnalAll), "all");
        alphaMat = ones(inputSize, outputSize) * alpha;
        betaMat = zeros(inputSize, outputSize);
        gammaMat = zeros(inputSize, outputSize);
        deltaMat = zeros(1, outputSize);
    end
    
    outputDigitAll = NaN(testNum, outputSize);
    alphaWeightAll = NaN(testNum, outputSize);
    betaWeightAll = NaN(testNum, outputSize);
    gammaWeightAll = NaN(testNum, outputSize);
    deltaWeightAll = NaN(testNum, outputSize);
    for testIdx = round(ratio*testNum)+1: testNum
        for outputIdx = 1: outputSize
            input = inputAll(testIdx, :);
            weight = squeeze(weightAll(testIdx, :, outputIdx));
    
            alphaWeight = 0;
            betaWeight = 0;
            gammaWeight = 0;
            deltaWeight = deltaMat(outputIdx);
            for inputIdx = 1: inputSize
                alphaWeight = alphaWeight + alphaMat(inputIdx, outputIdx) .* weight(inputIdx) .* input(inputIdx);
                betaWeight = betaWeight + betaMat(inputIdx, outputIdx) .* weight(inputIdx);
                deltaWeight = gammaMat(inputIdx, outputIdx) .* input(inputIdx);
            end
            alphaWeightAll(testIdx, outputIdx) = abs(alphaWeight);
            betaWeightAll(testIdx, outputIdx) = abs(betaWeight);
            gammaWeightAll(testIdx, outputIdx) = abs(gammaWeight);
            deltaWeightAll(testIdx, outputIdx) = abs(deltaWeight);
            outputDigitAll(testIdx, outputIdx) = abs(alphaWeight+betaWeight+gammaWeight+deltaWeight);
        end
    end
    figure(1);
    scatter(abs(outputDigitAll), abs(outputAnalAll));

    pearMat(inputSizeIdx) = mean(CalcPearson(abs(outputDigitAll(round(ratio*testNum)+1: testNum, :)).', abs(outputAnalAll(round(ratio*testNum)+1: testNum, :)).'));
    rmseMat(inputSizeIdx) = mean(CalcRMSE(abs(outputDigitAll(round(ratio*testNum)+1: testNum, :)).', abs(outputAnalAll(round(ratio*testNum)+1: testNum, :)).'));

    figure(11);
    plot(inputSizeList, pearMat);
    xlabel("Input Size");
    ylabel("Pearson");

    figure(12);
    plot(inputSizeList, rmseMat);
    xlabel("Input Size");
    ylabel("Pearson");
end