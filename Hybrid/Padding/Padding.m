clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

param = GetParam();

batchNum = 10;
inputSize = 1000;
outputSize = 100;
testNum = 5;

guardInputList = [0.5 0.2 0.1 0.05 0.02 0.01 0.005 0.002 0.001 0];
guardOutputList = [0.5 0.2 0.1 0.05 0.02 0.01 0.005 0.002 0.001 0];
guardDCList = [0.05 0.02 0.01 0.005 0.002 0.001 1e-5 0];

%% Guard Input

rmseMat = NaN(length(guardInputList), testNum);
pearMat = NaN(length(guardInputList), testNum);
for testIdx = 1: testNum
    for guardInputIdx = 1: length(guardInputList)
        param.guardInput = guardInputList(guardInputIdx);
        param.guardOutput = guardOutputList(2);
        param.guardDC = 1e-5;

        input = randn(batchNum, inputSize) .* exp(1i*2*pi*rand(batchNum, inputSize));
        weight = randn(batchNum, inputSize, outputSize) .* exp(1i*2*pi*rand(batchNum, inputSize, outputSize));
        outputDigitList = zeros(batchNum, outputSize);
        for batchIdx = 1: batchNum
            outputDigitList(batchIdx, :) = input(batchIdx, :) * reshape(weight(batchIdx, :, :), inputSize, outputSize);
        end
        
        outputAnalList = LayerFC(input, weight, "auto", param);
        
        outputDigit = abs(reshape(outputDigitList, 1, []));
        outputAnal = abs(reshape(outputAnalList, 1, []));
        pearson = CalcPearson(abs(outputDigit), abs(outputAnal));
        rmse = CalcRMSE(abs(outputDigit), abs(outputAnal));

        rmseMat(guardInputIdx, testIdx) = rmse;
        pearMat(guardInputIdx, testIdx) = pearson;
        
        figure(82);
        scatter(outputDigit, outputAnal);
        title("RMSE: "+rmse+" Pear: "+pearson);
        xlabel("Digital Computing");
        ylabel("Analog Computing");
        
        figure(83);
        plot(angle(outputAnalList./outputDigitList).');
        ylim([-pi +pi]);

        figure(1);
        subplot(2, 1, 1);
        heatmap(guardInputList, 1: testNum, rmseMat.');
        title("RMSE");
        subplot(2, 1, 2);
        heatmap(guardInputList, 1: testNum, pearMat.');
        title("Pearson");
        saveas(gcf, "Result/GuardInput_"+inputSize+"_"+outputSize+".png");

        figure(2);
        subplot(2, 1, 1);
        semilogx(guardInputList, mean(rmseMat, 2, "omitnan"));
        title("RMSE");
        subplot(2, 1, 2);
        semilogx(guardInputList, mean(pearMat, 2, "omitnan"));
        title("Pearson");
    end
end

%% Guard Output

rmseMat = NaN(length(guardOutputList), testNum);
pearMat = NaN(length(guardOutputList), testNum);
for testIdx = 1: testNum
    for guardOutputIdx = 1: length(guardOutputList)
        param.guardInput = guardInputList(2);
        param.guardOutput = guardOutputList(guardOutputIdx);
        param.guardDC = 1e-5;

        input = randn(batchNum, inputSize) .* exp(1i*2*pi*rand(batchNum, inputSize));
        weight = randn(batchNum, inputSize, outputSize) .* exp(1i*2*pi*rand(batchNum, inputSize, outputSize));
        outputDigitList = zeros(batchNum, outputSize);
        for batchIdx = 1: batchNum
            outputDigitList(batchIdx, :) = input(batchIdx, :) * reshape(weight(batchIdx, :, :), inputSize, outputSize);
        end
        
        outputAnalList = LayerFC(input, weight, "auto", param);
        
        outputDigit = abs(reshape(outputDigitList, 1, []));
        outputAnal = abs(reshape(outputAnalList, 1, []));
        pearson = CalcPearson(abs(outputDigit), abs(outputAnal));
        rmse = CalcRMSE(abs(outputDigit), abs(outputAnal));

        rmseMat(guardOutputIdx, testIdx) = rmse;
        pearMat(guardOutputIdx, testIdx) = pearson;
        
        figure(82);
        scatter(outputDigit, outputAnal);
        title("RMSE: "+rmse+" Pear: "+pearson);
        xlabel("Digital Computing");
        ylabel("Analog Computing");
        
        figure(83);
        plot(angle(outputAnalList./outputDigitList).');
        ylim([-pi +pi]);

        figure(1);
        subplot(2, 1, 1);
        heatmap(guardOutputList, 1: testNum, rmseMat.');
        title("RMSE");
        subplot(2, 1, 2);
        heatmap(guardOutputList, 1: testNum, pearMat.');
        title("Pearson");
        saveas(gcf, "Result/GuardOutput_"+inputSize+"_"+outputSize+".png");

        figure(2);
        subplot(2, 1, 1);
        semilogx(guardOutputList, mean(rmseMat, 2, "omitnan"));
        title("RMSE");
        subplot(2, 1, 2);
        semilogx(guardOutputList, mean(pearMat, 2, "omitnan"));
        title("Pearson");
    end
end

%% Guard DC

rmseMat = NaN(length(guardDCList), testNum);
pearMat = NaN(length(guardDCList), testNum);
for testIdx = 1: testNum
    for guardDCIdx = 1: length(guardDCList)
        param.guardInput = guardInputList(2);
        param.guardOutput = guardOutputList(2);
        param.guardDC = guardDCList(guardDCIdx);

        input = randn(batchNum, inputSize) .* exp(1i*2*pi*rand(batchNum, inputSize));
        weight = randn(batchNum, inputSize, outputSize) .* exp(1i*2*pi*rand(batchNum, inputSize, outputSize));
        outputDigitList = zeros(batchNum, outputSize);
        for batchIdx = 1: batchNum
            outputDigitList(batchIdx, :) = input(batchIdx, :) * reshape(weight(batchIdx, :, :), inputSize, outputSize);
        end
        
        outputAnalList = LayerFC(input, weight, "auto", param);
        
        outputDigit = abs(reshape(outputDigitList, 1, []));
        outputAnal = abs(reshape(outputAnalList, 1, []));
        pearson = CalcPearson(abs(outputDigit), abs(outputAnal));
        rmse = CalcRMSE(abs(outputDigit), abs(outputAnal));

        rmseMat(guardDCIdx, testIdx) = rmse;
        pearMat(guardDCIdx, testIdx) = pearson;
        
        figure(82);
        scatter(outputDigit, outputAnal);
        title("RMSE: "+rmse+" Pear: "+pearson);
        xlabel("Digital Computing");
        ylabel("Analog Computing");
        
        figure(83);
        plot(angle(outputAnalList./outputDigitList).');
        ylim([-pi +pi]);

        figure(1);
        subplot(2, 1, 1);
        heatmap(guardDCList, 1: testNum, rmseMat.');
        title("RMSE");
        subplot(2, 1, 2);
        heatmap(guardDCList, 1: testNum, pearMat.');
        title("Pearson");
        saveas(gcf, "Result/GuardDC_"+inputSize+"_"+outputSize+".png");

        figure(2);
        subplot(2, 1, 1);
        semilogx(guardDCList, mean(rmseMat, 2, "omitnan"));
        title("RMSE");
        subplot(2, 1, 2);
        semilogx(guardDCList, mean(pearMat, 2, "omitnan"));
        title("Pearson");
    end
end