clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

testNum = 10000;
batchNum = 10000;
inputSizeList = [300]; % [100 300 784 1000 4000];
outputSize = 10;

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

    scalar = 1*inputSize*inputSize*outputSize;
    inputAll = load("dataset/dataIn_"+inputSize+"_"+outputSize+".mat").inputAll;
    weightAll = load("dataset/dataIn_"+inputSize+"_"+outputSize+".mat").weightAll;
    outputAnalAll = abs(load("dataset/dataOut_"+inputSize+"_"+outputSize+".mat").outputAnalAll);
    
    cacheName = "./Result/result_"+inputSize+"_"+outputSize+"_one/result.mat";
    if exist(cacheName, 'file')
        csiMat = load(cacheName).alphaMat;
    else
        alpha = 1; % mean(abs(outputDigitAll), "all") / mean(abs(outputAnalAll), "all");
        csiMat = ones(inputSize, outputSize) * alpha;
    end

    csi = mean(abs(csiMat(:, 2: end-1)), 2);
    phase = mean(unwrap(angle(csiMat(round(0.1*inputSize): round(0.9*inputSize), 2: end-1))), 2);
    coeff = polyfit((round(0.1*inputSize): round(0.9*inputSize))/inputSize, phase, 1);
    slope = coeff(1);
    figure(1);
    plot((1: inputSize)/inputSize, abs(csiMat));
    hold on;
    plot((1: inputSize)/inputSize, csi, 'LineWidth', 2);
    hold off;
    figure(2);
    plot((1: inputSize)/inputSize, angle(csiMat));
    hold on;
    plot((1: inputSize)/inputSize, (1: inputSize)/inputSize*slope, 'LineWidth', 2);
    hold off;
    title("Slope: "+slope);
    save("Cache/channel_"+inputSize+".mat", "csi", "slope");
    csi = reshape(csiMat.', 1, []);
    save("Cache/channel_"+inputSize+".mat", "csi");
    
    outputDigitAll = NaN(testNum, outputSize);
    for testIdx = round(ratio*testNum)+1: testNum
        for outputIdx = 1: outputSize
            input = inputAll(testIdx, :);
            weight = squeeze(weightAll(testIdx, :, outputIdx));
    
            outputDigitAll(testIdx, outputIdx) = 0;
            for inputIdx = 1: inputSize
                outputDigitAll(testIdx, outputIdx) = outputDigitAll(testIdx, outputIdx) + ...
                    csiMat(inputIdx, outputIdx) .* weight(inputIdx) .* input(inputIdx);
            end
        end
    end
    figure(3);
    scatter(abs(outputDigitAll), abs(outputAnalAll));

    pearMat(inputSizeIdx) = mean(CalcPearson(abs(outputDigitAll(round(ratio*testNum)+1: testNum, :)).', abs(outputAnalAll(round(ratio*testNum)+1: testNum, :)).'));
    rmseMat(inputSizeIdx) = mean(CalcRMSE(abs(outputDigitAll(round(ratio*testNum)+1: testNum, :)).', abs(outputAnalAll(round(ratio*testNum)+1: testNum, :)).'));

%     figure(11);
%     plot(inputSizeList, pearMat);
%     xlabel("Input Size");
%     ylabel("Pearson");
% 
%     figure(12);
%     plot(inputSizeList, rmseMat);
%     xlabel("Input Size");
%     ylabel("Pearson");
end