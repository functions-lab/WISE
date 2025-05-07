clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(1);

%%

testNum = 1000;
batchNum = 1000;
inputSizeList = [300];
outputSize = 10;
outputUsed = 1: outputSize-1;
token = "corner3";

param = GetParam_low();
param.gainTx = [14 30];
param.encMode = "freq"; % Different!!!
param.decMode = "freq";
% param.inputNorm = NaN;
% param.weightNorm = NaN;
% param.delay = 0.85;

param.guardInput = 0;
param.guardOutput = 0;
param.guardDC = 0;

%%

for inputSize = inputSizeList
    inputAll = rand(testNum, inputSize) .* exp(1i*2*pi*rand(testNum, inputSize)) *sqrt(inputSize)*outputSize*5/9;
    weightAll = rand(testNum, inputSize, outputSize) .* exp(1i*2*pi*rand(testNum, inputSize, outputSize)) *sqrt(inputSize*outputSize)*5/9;
    
    cacheName = "./Result/result_"+inputSize+"_"+outputSize+"_one_"+token+"/result.mat";
    if exist(cacheName, 'file')
        csiMat = load(cacheName).alphaMat;
        csiMat = csiMat ./ mean(abs(csiMat), 'all');
%         csiMat(:, end) = 1;
    else
        alpha = 1; % mean(abs(outputDigitAll), "all") / mean(abs(outputAnalAll), "all");
        csiMat = ones(inputSize, outputSize) * alpha;
    end
    
    resp = mean(abs(csiMat(:, outputUsed)), 2);
    phase = mean(unwrap(angle(csiMat(round(0.1*inputSize): round(0.9*inputSize), outputUsed))), 2);
    coeff = polyfit((round(0.1*inputSize): round(0.9*inputSize))/inputSize, phase, 1);
    slope = coeff(1);
    figure(11);
    plot((1: inputSize)/inputSize, abs(csiMat));
    hold on;
    plot((1: inputSize)/inputSize, resp, 'LineWidth', 2);
    hold off;
    saveas(gcf, "Cache/channel_"+inputSize+"_"+token+"_amp.png");
    figure(12);
    plot((1: inputSize)/inputSize, angle(csiMat));
    hold on;
    plot((1: inputSize)/inputSize, (1: inputSize)/inputSize*slope, 'LineWidth', 2);
    hold off;
    title("Slope: "+slope);
    saveas(gcf, "Cache/channel_"+inputSize+"_"+token+"_phase.png");
    save("Cache/channel_"+inputSize+"_"+token+".mat", "resp", "slope");
    
%     csi = reshape(csiMat.', 1, []);
%     save("Cache/channel_"+inputSize+".mat", "csi");
    
    %%
    
    for testIdx = 1: floor(testNum/batchNum)
        disp(testIdx*batchNum+"/"+testNum);
        
        startIdx = (testIdx-1) * batchNum + 1;
        endIdx = testIdx * batchNum;
        inputList = inputAll(startIdx: endIdx, :, :);
        weightList = weightAll(startIdx: endIdx, :, :);
                
        outputDigitList = NaN(batchNum, outputSize);
        weightCalList = NaN(batchNum, inputSize, outputSize);
        for batchIdx = 1: batchNum
            outputDigitList(batchIdx, :) = inputList(batchIdx, :) * reshape(weightList(batchIdx, :, :), inputSize, outputSize);
            weightCalList(batchIdx, :, :) = reshape(weightList(batchIdx, :, :), inputSize, outputSize) ./ csiMat;
    %         outputDigitList(batchIdx, :) = inputList(batchIdx, :) * (reshape(weightList(batchIdx, :, :), inputSize, outputSize).*csiMat);
    %         weightCalList(batchIdx, :, :) = reshape(weightList(batchIdx, :, :), inputSize, outputSize);
        end
    
        outputAnalList = LayerFC(inputList, weightCalList, "auto", param);
        outputAnalList = squeeze(outputAnalList);
%         outputAnalList = outputAnalList(:, 1: end-1);
%         outputDigitList = outputDigitList(:, 1: end-1);
        pearson = CalcPearson(abs(outputDigitList), abs(outputAnalList));
        rmse = CalcRMSE(abs(outputDigitList), abs(outputAnalList));
    
        figure(1);
        hold on;
        for outputIdx = 1: outputSize
            scatter(abs(outputDigitList(:, outputIdx)), abs(outputAnalList(:, outputIdx)));
        end
        hold off;
        title("RMSE: "+mean(rmse)+" Pear: "+mean(pearson));
        xlabel("Digital Computing");
        ylabel("Analog Computing");
    end
end