clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

datasetList = ["MNIST", "Audio"]; % ["MNIST", "SVHN", "Audio", "FMNIST"]
modelList = ["FC3"];

param = GetParam_low();

% vvv For Wireless Setting vvv
param.gainTx = [7 31];
powerLO = -3.04 + 11;
userNum = 3;
param.calib = [];
param.calib = [ ...
    "/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300_corner1.mat" ...
    "/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300_corner2.mat" ...
    "/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300_corner3.mat"];
% userNum = 1;
% param.calib = [ ...
%     "/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300_user1.mat"];
param.precode = "weight";
param.encMode = "time";
% ^^^ For Wireless Setting ^^^

% % vvv For Wired Setting vvv
% param.gainTx = [9 19];
% powerLO = -3.04;
% param.calib = "/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300_wired.mat";
% param.precode = "input";
% % ^^^ For Wired Setting ^^^

param.userNum = userNum;

param.decMode = "split-1";
param.padRate = 0; % 0.5;
param.cpRate = 0; % -1;
param.batchInOutProd = 100000000;
param.batchOutProd = 100000; % NOT effective for param.decMode = "freq";

powerList = -45: -1: -75;
token = "fine";

param.transMode = "exp";

param.subMax = 1000000;
param.subMin = 1;
param.guardDC = 1e-5;
param.guardInput = 0.05;
param.guardOutput = 0.1;
param.inputNorm = -0.2;
param.weightNorm = -0.2;

offsetInput = -21.98;
offsetWeight = -22.04;
attenInput = -30;
attenWeight = -0;

powerNum = length(powerList);
resultPath = "NopadPreW_"+param.encMode+"-"+param.decMode+"/";

act = "zadoff";
method = "auto";
classNum = 10;

if ~isfolder(resultPath)
    mkdir(resultPath);
end
for dataset = datasetList
    if(dataset == "Audio")
        dataType = "stft-zadoff-200";
    else
        dataType = "zadoff";
    end
    for model = modelList
        if exist(resultPath+dataset+"_"+model+"_"+token+".mat", "file")
            continue;
        end

        folderList = dir("../../ML/Result/");
        folderNum = 0;
        for folderIdx = 1: length(folderList)
            folder = string(folderList(folderIdx).name);
            if(startsWith(folder, dataset))&&(endsWith(folder, model))
                folderNum = folderNum + 1;
                folderName = folder;
                disp(folderName);
            end
        end
        if folderNum ~= 1
            disp("Warning: Folder NOT Found!");
            continue;
        end
        modelFile = "../../ML/Result/"+folderName+"/model_accMax.mat";
        posStart = strfind(folderName, "size")+4;
        posEnd = strfind(folderName, model) - 2;
        folderChar = char(folderName);
        dataSize = string(folderChar(posStart: posEnd));
        dataFile = "../../ML/Data/Data_"+dataset+"_"+dataType+"_"+dataSize+".mat";

        result = load(modelFile);
        index = 0;
        FCList = {};
        macNum = 0;
        hiddenIdx = 1;
        while isfield(result, "Matrix_"+hiddenIdx)
            FCList{end+1} = double(result.("Matrix_"+hiddenIdx).'); %#ok<SAGROW>
            macNum = macNum + size(result.("Matrix_"+hiddenIdx).', 1) * size(result.("Matrix_"+hiddenIdx).', 2);
            hiddenIdx = hiddenIdx + 1;
        end
        CONVList = {};

        dataList = load(dataFile).dataList;
        targetList = load(dataFile).targetList;
        dataNum = length(targetList);

        % Digital Computing
        matDigit = zeros(classNum, classNum);
        for dataIdx = 1: dataNum
            data = squeeze(dataList(dataIdx, :, :));
            target = targetList(dataIdx)+1;
        
            predVec = DigitalInference(data, CONVList, -1, FCList, act);
            [~, predMax] = max(predVec);
            matDigit(predMax, target) = matDigit(predMax, target) + 1;
            accDigit = trace(matDigit) / sum(matDigit, 'all');
        end
        
%         figure(1);
%         heatmap((1: classNum)-1, (1: classNum)-1, matDigit);
%         title("Digital ACC: "+accDigit);
%         saveas(gcf, ResultPath+dataset+"_"+FCNum+"_digital_"+token+".png");

        % Analog Computing
        batchNum = dataNum;
        matAnalList = zeros(userNum, powerNum, classNum, classNum);
        accAnalList = NaN(userNum, powerNum);
        for batchIdx = 1: ceil(dataNum/batchNum)
            startIdx = (batchIdx-1) * batchNum + 1;
            endIdx = min(batchIdx * batchNum, dataNum);
        
            data = dataList(startIdx: endIdx, :, :);
            target = targetList(startIdx: endIdx)+1;
            
            for powerIdx = 1: powerNum
                ampInput = sqrt(Gain2Power(powerList(powerIdx)-offsetInput-attenInput-param.gainTx(1)));
                ampWeight = sqrt(Gain2Power(powerLO-offsetWeight-attenWeight-param.gainTx(2)));
                param.inputNorm = -0.2 * ampInput;
                param.weightNorm = -0.2 * ampWeight;

                [predVec, waveTime] = AnalogInference(data, CONVList, -1, FCList, act, method, param);
                emacList = 10.^(powerList/10)/1000 * waveTime / macNum / batchNum;
                [~, predMax] = max(predVec, [], 3);

                matNow = zeros(userNum, classNum, classNum);
                for dataIdx = 1: endIdx-startIdx+1
                    targetNow = target(dataIdx);
                    for userIdx = 1: userNum
                        matNow(userIdx, predMax(userIdx, dataIdx), targetNow) = ...
                            matNow(userIdx, predMax(userIdx, dataIdx), targetNow) + 1;
                    end
                end

                figure(1);
                for userIdx = 1: userNum
                    matAnalList(userIdx, powerIdx, :, :) = ...
                        matAnalList(userIdx, powerIdx, :, :) + reshape(matNow(userIdx, :, :), [1 1 classNum classNum]);
                    accAnalList(userIdx, powerIdx) = ...
                        trace(reshape(matAnalList(userIdx, powerIdx, :, :), [classNum classNum])) / ...
                        sum(matAnalList(userIdx, powerIdx, :, :), 'all');
    
                    plot(emacList, accAnalList(userIdx, :), '+-');
                    hold on;
                end
                hold off;
                yline(accDigit);
                set(gca, 'XScale', 'log');
                xlabel("E_{MAC} J/MAC");
                xlim([min(emacList)/2 max(emacList)*2]);
                ylabel("Accuracy");
                ylim([0 1]);
                title(dataset+" "+model+" ("+batchIdx*batchNum+"/"+dataNum+")");
                saveas(gcf, resultPath+dataset+"_"+model+"_curve_"+token+".png");
                save(resultPath+dataset+"_"+model+"_"+token+".mat", ...
                    "powerList", "emacList", "matDigit", "accDigit", "matAnalList", "accAnalList");
            end
        end
    end
end
