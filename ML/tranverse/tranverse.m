clear;
clc;
close all;

%%

testNum = 5;
setting = "cross-log_conv";
hiddenList = ["-1", "10", "20", "50", "100", "50,20"];

accMat = NaN(length(hiddenList), testNum);
for hiddenIdx = 1: length(hiddenList)
    hidden = hiddenList(hiddenIdx);

    for testIdx = 1: testNum
        result = load("../Result/MNIST_size14_"+setting+"_"+hidden+"_"+testIdx+"/model_accMax.mat");
        accMat(hiddenIdx, testIdx) = max(result.accTest);
    end
end

figure(1);
heatmap(1: testNum, hiddenList, accMat);