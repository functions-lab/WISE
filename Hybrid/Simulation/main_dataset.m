clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

param = GetParam();
param.encMode = "time";
param.decMode = "split-4";
powerList = -70: -2: -110;

param.transMode = "fast";
param.sampleRate = 100e6;

param.subMax = +inf;
param.subMin = 1;
param.cpRate = -1; % -1 for automatic, only include the first lobe of sinc function
param.guardInput = 1e-10;
param.guardOutput = 1e-10;
param.guardDC = 0;

param.boltzmann = physconst("Boltzmann");
param.temperature = 300;
param.insertion = 0; % 11.97;
param.noisefigure = 0; % 13.32;

powerLO = -3.56;
powerNum = length(powerList);
resultPath = "Result_"+param.encMode+"-"+param.decMode+"/";

act = "zadoff";
method = "auto";
classNum = 10;
batchNum = 100;

if ~exist(resultPath, "dir")
    mkdir(resultPath);
end
for dataset = ["MNIST", "SVHN", "Audio", "FMNIST"]
    if(dataset == "Audio")
        dataType = "stft-zadoff-200";
    else
        dataType = "zadoff";
    end
    for token = ["FC1", "FC2", "FC3"]
%     for token = ["FC4"]
        if exist(resultPath+dataset+"_"+token+".mat", "file")
            continue;
        end

        folderList = dir("../../ML/Result/");
        folderNum = 0;
        for folderIdx = 1: length(folderList)
            folder = string(folderList(folderIdx).name);
            if(startsWith(folder, dataset))&&(endsWith(folder, token))
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
        posEnd = strfind(folderName, token) - 2;
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
        predTrue = NaN(dataNum, 1);
        predFalse = NaN(dataNum, classNum-1);
        for dataIdx = 1: dataNum
            data = squeeze(dataList(dataIdx, :, :));
            target = targetList(dataIdx)+1;
        
            predVec = DigitalInference(data, CONVList, -1, FCList, act);
            [~, predMax] = max(predVec);
        
            predTrue(dataIdx, 1) = predVec(target);
            predFalse(dataIdx, :) = predVec([1: target-1 target+1: classNum]);
        
            matDigit(predMax, target) = matDigit(predMax, target) + 1;
            accDigit = trace(matDigit) / sum(matDigit, 'all');
        end
        
%         figure(1);
%         heatmap((1: classNum)-1, (1: classNum)-1, matDigit);
%         title("Digital ACC: "+accDigit);
%         saveas(gcf, "Result_energy/"+dataset+"_"+FCNum+"_digital_"+token+".png");

        % Analog Computing
        matAnalList = zeros(powerNum, classNum, classNum);
        accAnalList = NaN(1, powerNum);
        predTrue = NaN(dataNum, 1);
        predFalse = NaN(dataNum, classNum-1);
        for batchIdx = 1: ceil(dataNum/batchNum)
            startIdx = (batchIdx-1) * batchNum + 1;
            endIdx = min(batchIdx * batchNum, dataNum);
        
            data = dataList(startIdx: endIdx, :, :);
            target = targetList(startIdx: endIdx)+1;
            
            for powerIdx = 1: powerNum
                param.powerRF = powerList(powerIdx);
                param.powerLO = powerLO;

                [predVec, waveTime] = AnalogInference(data, CONVList, -1, FCList, act, method, param);
                emacList = 10.^(powerList/10)/1000 * waveTime / macNum / batchNum;
                [~, predMax] = max(predVec, [], 2);

                matNow = zeros(classNum, classNum);
                for dataIdx = 1: endIdx-startIdx+1
                    targetNow = target(dataIdx);
            
                    predTrue((batchIdx-1)*batchNum+dataIdx, 1) = predVec(dataIdx, targetNow);
                    predFalse((batchIdx-1)*batchNum+dataIdx, :) = predVec(dataIdx, [1: targetNow-1 targetNow+1: classNum]);
            
                    matNow(predMax(dataIdx), targetNow) = matNow(predMax(dataIdx), targetNow) + 1;
                end
                accNow = trace(matNow) / sum(matNow, 'all');
                matAnalList(powerIdx, :, :) = matAnalList(powerIdx, :, :) + reshape(matNow, [1 classNum classNum]);
                accAnalList(powerIdx) = ...
                    trace(reshape(matAnalList(powerIdx, :, :), [classNum classNum])) / sum(matAnalList(powerIdx, :, :), 'all');
            end
            figure(1);
            plot(emacList, 1-accAnalList, '+-');
            hold on;
            yline(1-accDigit);
            hold off;
            set(gca, 'XScale', 'log');
            xlabel("E_{MAC} J/MAC");
            ylabel("Error Rate");
            ylim([0 1]);
            title(dataset+" "+token+" ("+batchIdx*batchNum+"/"+dataNum+")");
            saveas(gcf, resultPath+dataset+"_"+token+"_curve.png");
            save(resultPath+dataset+"_"+token+".mat", ...
                "powerList", "emacList", "matDigit", "accDigit", "matAnalList", "accAnalList");
        end
    end
end