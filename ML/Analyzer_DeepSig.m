clear;
clc;
close all;
rng(0);

%%

moduList = ["BPSK", "QPSK", "16QAM", "64QAM"];
sizeList = [256, 1024, 1024, 1024, 1024, 1024];
tokenList = ["conv7-fc3-b1", "conv7-fc3-b1", "ours-abs-c64", "ours-abs-c64", "ours-abs-c64", "ours-abs-c64"];

resultNum = min(length(sizeList), length(tokenList));

%%

for resultIdx = 1: resultNum
    size = sizeList(resultIdx);
    token = tokenList(resultIdx);
    resultPath = "./Result/DeepSig_size"+size+"_"+token+"/";
    if ~exist(resultPath, "dir")
        disp(resultPath);
        continue;
    end

    result = load(resultPath+"model_accMax.mat");

    figure;
    heatmap(moduList, moduList, squeeze(result.matTest(end, end, :, :)));
    xlabel("Actual");
    ylabel("Predicted");
    title(token+" acc: "+result.accTest(end, end));

    figure;
    plot(result.snrSet, result.accTest(end, :));
end