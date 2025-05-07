clear;
clc;
close all;
addpath(genpath("../Library"));
% addpath(genpath("./Core"));
rng(0);

%%

DATA = "MNIST";
TYPE = "zadoff";
TOKEN = "best";
EPOCH = 1000;

symNum = 100;
imageSize = 14;
classNum = 10;
inputSize = 200;

inputNorm = 1;
weightNorm = 1;
cacheName = ""; %  "../FC_general_SA/version_2/result_small/result.mat";

%%

if exist(cacheName, 'file')
    alphaMat = load(cacheName).alphaMat;
else
    alphaMat = ones(inputSize, classNum);
end

dataFile = load("../ML/Data/Data_"+DATA+"_"+TYPE+".mat");
targetAll = dataFile.targetList;
dataTemp = dataFile.dataList;
dataNum = size(dataTemp, 1);
dataSize = round(numel(dataTemp)/dataNum);
dataAll = NaN(dataNum, dataSize);
for dataIdx = 1: dataNum
    dataAll(dataIdx, :) = reshape(squeeze(dataTemp(dataIdx, :, :)).', 1, dataSize) / inputNorm;
end
dataTemp = reshape(dataTemp, dataNum, []);
dataSize = size(dataTemp, 2);

classMatGt = NaN(EPOCH, dataNum, classNum);
classListTrue = NaN(EPOCH, dataNum);
classListFalse = NaN(EPOCH, dataNum, (classNum-1));
for epochIdx = 1: EPOCH
    if ~ isfile("../ML/Result/MNIST_size"+imageSize+"_"+TOKEN+"/model_"+(epochIdx-1)+".mat")
        break;
    end
    weightFile = load("../ML/Result/MNIST_size"+imageSize+"_"+TOKEN+"/model_"+(epochIdx-1)+".mat");
    weightMat = weightFile.Matrix_1 / weightNorm ./ alphaMat(1: dataSize, :);
    
    for dataIdx = 1: dataNum
        classVec= abs(dataAll(dataIdx, :) * weightMat);
        classMatGt(epochIdx, dataIdx, :) = classVec;
        classListTrue(epochIdx, dataIdx) = classVec(targetAll(dataIdx)+1);
        classVec(targetAll(dataIdx)+1) = [];
        classListFalse(epochIdx, dataIdx, :) = classVec;
    end
    epochNum = epochIdx;
end

figure(1);
for dataIdx = 1: 4*8
    subplot(4, 8, dataIdx);
    plot(squeeze(classMatGt(:, dataIdx, :)));
    hold on;
    plot(squeeze(classMatGt(:, dataIdx, targetAll(dataIdx)+1)), 'LineWidth', 2);
%     ylim([0 2]);
end

figure(2);
subplot(2, 1, 1);
histogram(reshape(classListTrue(epochNum, :), [], 1), 100);
xlim([0 2]);
subplot(2, 1, 2);
histogram(reshape(classListFalse(epochNum, :, :), [], 1), 100);
xlim([0 2]);