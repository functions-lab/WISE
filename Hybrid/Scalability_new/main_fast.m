clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

testNum = 1;
batchNum = 200;
% inputSizeList = [50000];
inputSizeList = [64 128 256 512 1024 2048 4096 8192 16384 32768]; % [100, 300, 1000, 3000, 10000, 30000]; % 
outputSize = 1; % 6;

param = GetParam();

% vvv For Wireless Setting vvv
param.gainTx = [14 30];
powerLO = -3.04 + 11;
calib = "/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300.mat";
param.precode = "weight";
% ^^^ For Wireless Setting ^^^

% % vvv For Wired Setting vvv
% param.gainTx = [14 19];
% powerLO = -3.04;
% calib = "";
% % ^^^ For Wired Setting ^^^

param.encMode = "time";
% param.decMode = "split-"+outputSize;
param.decMode = "split-1";
param.padRate = 0.333; % new

powerList = -30: -0.2: -70;

param.sampleRate = 100e6;

param.subMax = 1000000;
param.subMin = 1;
param.guardDC = 1e-5;
param.guardInput = 0.05;
param.guardOutput = 0.1;
param.attenList = powerList(1) - powerList;

% Simulation
param.powerRF = powerList(1);
param.powerLO = powerLO;

offsetInput = -21.98;
offsetWeight = -22.04;
attenInput = -30;
attenWeight = -0;
% Experiment
param.inputNorm = 0.2 * sqrt(Gain2Power(powerList(1)-offsetInput-attenInput-param.gainTx(1))); % Different from Dataset!
param.weightNorm = 0.2 * sqrt(Gain2Power(powerLO-offsetWeight-attenWeight-param.gainTx(2))); % Different from Dataset!

powerNum = length(powerList);
resultPath = "WirelessPreWWW_"+param.encMode+"-"+param.decMode+"/";

method = "auto";

if ~isfolder(resultPath)
    mkdir(resultPath);
end
for inputSizeIdx = 1: length(inputSizeList)
    inputSize = inputSizeList(inputSizeIdx);

    if exist(resultPath+"Result_"+inputSize+".mat", "file")
        continue;
    end

    pearMat_sim = NaN(testNum, length(powerList));
    rmseMat_sim = NaN(testNum, length(powerList));
    pearMat_exp = NaN(testNum, length(powerList));
    rmseMat_exp = NaN(testNum, length(powerList));
    outputDigitMat = NaN(testNum, batchNum, outputSize);
    outputAnalMat_sim = NaN(testNum, length(powerList), batchNum, outputSize);
    outputAnalMat_exp = NaN(testNum, length(powerList), batchNum, outputSize);
    for testIdx = 1: testNum
        disp("Test: "+testIdx+"/"+testNum);

        input = rand(batchNum, inputSize) .* exp(1i*2*pi*rand(batchNum, inputSize));
        weight = rand(batchNum, inputSize, outputSize) .* exp(1i*2*pi*rand(batchNum, inputSize, outputSize));
        outputDigit = NaN(batchNum, outputSize);
        for batchIdx = 1: batchNum
            outputDigit(batchIdx, :) = input(batchIdx, :) * reshape(weight(batchIdx, :, :), [inputSize, outputSize]);
        end
        outputDigitMat(testIdx, :, :) = outputDigit;

%         % Simulation
%         param.transMode = "easy";
%         param.calib = "";
%         [outputAnalList_sim, ~, waveTime_sim] = LayerFC(input, weight, method, param);
%         outputAnalMat_sim(testIdx, :, :, :) = outputAnalList_sim;
%         for powerIdx = 1: length(powerList)
%             outputAnal_sim = reshape(outputAnalList_sim(powerIdx, :, :), [batchNum outputSize]);
%             pear_sim = mean(CalcPearson(abs(outputDigit).', abs(outputAnal_sim).'));
%             pearMat_sim(testIdx, powerIdx) = pear_sim;
%             rmse_sim = mean(CalcRMSE(abs(outputDigit).', abs(outputAnal_sim).'));
%             rmseMat_sim(testIdx, powerIdx) = rmse_sim;
%             emacList_sim = 10.^(powerList/10)/1000 * waveTime_sim / inputSize / outputSize / batchNum;
%         end
% %         figure(51);
% %         scatter(abs(outputDigit), abs(outputAnalList_sim));
% %         title("Pearson: "+pear_sim+" RMSE: "+rmse_sim);
% %         xlabel("Digital Computing");
% %         ylabel("Analog Computing");
        emacList_sim = NaN(1, powerNum);


        % Experiment
        param.transMode = "exp";
        param.calib = calib;
        [outputAnalList_exp, ~, waveTime_exp] = LayerFC(input, weight, method, param);
        outputAnalMat_exp(testIdx, :, :, :) = outputAnalList_exp;
        for powerIdx = 1: length(powerList)
            outputAnal_exp = reshape(outputAnalList_exp(powerIdx, :, :), [batchNum outputSize]);
            pear_exp = mean(CalcPearson(abs(outputDigit).', abs(outputAnal_exp).'));
            pearMat_exp(testIdx, powerIdx) = pear_exp;
            rmse_exp = mean(CalcRMSE(abs(outputDigit).', abs(outputAnal_exp).'));
            rmseMat_exp(testIdx, powerIdx) = rmse_exp;
            emacList_exp = 10.^(powerList/10)/1000 * waveTime_exp / inputSize / outputSize / batchNum;
        end
%         figure(52);
%         scatter(abs(outputDigit), abs(outputAnal_exp));
%         title("Pearson: "+pear_exp+" RMSE: "+rmse_exp);
%         xlabel("Digital Computing");
%         ylabel("Analog Computing");
    
        figure(1);
        plot(emacList_sim, squeeze(median(rmseMat_sim, 1, 'omitnan')), '+-');
        hold on;
        plot(emacList_exp, squeeze(median(rmseMat_exp, 1, 'omitnan')), 'x');
        hold off;
        set(gca, 'XScale', 'log');
        xlabel("E_{MAC} J/MAC");
        xlim([min(emacList_exp)/2 max(emacList_exp)*2]);
        ylabel("RMSE");
        title("Input Size: "+inputSize+" ("+testIdx+"/"+testNum+")");
        saveas(gcf, resultPath+"Result_"+inputSize+"_RMSE.png");
        figure(2);
        plot(emacList_sim, squeeze(median(pearMat_sim, 1, 'omitnan')), '+-');
        hold on;
        plot(emacList_exp, squeeze(median(pearMat_exp, 1, 'omitnan')), 'x');
        hold off;
        set(gca, 'XScale', 'log');
        xlabel("E_{MAC} J/MAC");
        xlim([min(emacList_exp)/2 max(emacList_exp)*2]);
        ylabel("Pearson");
        title("Input Size: "+inputSize+" ("+testIdx+"/"+testNum+")");
        saveas(gcf, resultPath+"Result_"+inputSize+"_Pearson.png");
        save(resultPath+"Result_"+inputSize+".mat", ...
            "inputSizeList", "powerList", "emacList_sim", "emacList_exp", ...
            "pearMat_sim", "rmseMat_sim", "pearMat_exp", "rmseMat_exp", ...
            "outputDigitMat", "outputAnalMat_sim", "outputAnalMat_exp");
    end
end