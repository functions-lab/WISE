clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

batchNum = 100;
inputSizeList = [64 256 1024];
outputSize = 1;
powerRFList = [-43 -53 -63];
powerLOList = -10: 0.1: 0;

%%

powerLONum = length(powerLOList);
powerRFNum = length(powerRFList);

param = GetParam_low();
param.gainTx = [9 19];
param.userNum = 1;
param.calib = ["/home/zg88/CEI/Analog/Code/Hybrid/Calibration_new/Cache/channel_300_wired.mat"];
param.precode = "weight";
param.encMode = "time";
param.decMode = "split-1";

offsetInput = -22;
offsetWeight = -22;
attenInput = -30;
attenWeight = -0;
noise = 1.38e-23 * 300;
NF = 10^(25/10);

resultPath = "Wired_"+param.encMode+"-"+param.decMode+"/";

if ~isfolder(resultPath)
    mkdir(resultPath);
end
for inputSizeIdx = 1: length(inputSizeList)
    inputSize = inputSizeList(inputSizeIdx);
    if exist(resultPath+"Result_"+inputSize+".mat", "file")
        continue;
    end

    outputDigit = NaN(batchNum, outputSize);
    outputAnalMat = NaN(powerLONum, powerRFNum, batchNum, outputSize);
    emacList = NaN(powerLONum, powerRFNum);
    snrList = NaN(powerLONum, powerRFNum);
    pearMat = NaN(powerLONum, powerRFNum);
    rmseMat = NaN(powerLONum, powerRFNum);

    input = rand(batchNum, inputSize) .* exp(1i*2*pi*rand(batchNum, inputSize));
    weight = rand(batchNum, inputSize, outputSize) .* exp(1i*2*pi*rand(batchNum, inputSize, outputSize));
    for batchIdx = 1: batchNum
        outputDigit(batchIdx, :) = input(batchIdx, :) * reshape(weight(batchIdx, :, :), [inputSize, outputSize]);
    end

    for powerLOIdx = 1: powerLONum
        powerLO = powerLOList(powerLOIdx);
        param.weightNorm = 0.2 * sqrt(Gain2Power(powerLO-offsetWeight-attenWeight-param.gainTx(2)));

        for powerRFIdx = 1: powerRFNum
            powerRF = powerRFList(powerRFIdx);
            param.inputNorm = 0.2 * sqrt(Gain2Power(powerRF-offsetInput-attenInput-param.gainTx(1)));

            [outputAnal, ~, waveTime] = LayerFC(input, weight, "auto", param);
            outputAnal = reshape(outputAnal, [batchNum outputSize]);
            outputAnalMat(powerLOIdx, powerRFIdx, :, :) = outputAnal;

            emac = 10.^(powerRF/10)/1000 * waveTime / inputSize / outputSize / batchNum;
            emacList(powerLOIdx, powerRFIdx) = emac;
            snrList(powerLOIdx, powerRFIdx) = emac / noise / NF;
            pear = mean(CalcPearson(abs(outputDigit).', abs(outputAnal).'));
            pearMat(powerLOIdx, powerRFIdx) = pear;
            rmse = mean(CalcRMSE(abs(outputDigit).', abs(outputAnal).'));
            rmseMat(powerLOIdx, powerRFIdx) = rmse;
        
            figure(1);
            plot(powerLOList, rmseMat, '+-');
            xlabel("LO Power");
            ylabel("RMSE");
            title("Input Size: "+inputSize);
            saveas(gcf, resultPath+"Result_"+inputSize+"_RMSE.png");

            figure(2);
            plot(powerLOList, pearMat, '+-');
            xlabel("LO Power");
            ylabel("RMSE");
            title("Input Size: "+inputSize);
            saveas(gcf, resultPath+"Result_"+inputSize+"_RMSE.png");

            save(resultPath+"Result_"+inputSize+".mat", ...
                "powerLOList", "powerRFList", ...
                "outputDigit", "outputAnalMat", ...
                "emacList", "rmseMat", "pearMat");
        end
    end
end