clear;
clc;
close all;
addpath(genpath("../../Library"));
addpath(genpath("../Core"));
rng(0);

%%

band = 100e6;

for dataset = ["MNIST"] % ["MNIST", "SVHN", "FMNIST", "CIFAR-10"]
    figure(1);
    hold on;
    for FCNum = 1: 4
        if ~exist("Result_dataset_new/"+dataset+"_FC"+FCNum+".mat", "file")
            continue;
        end
        result = load("Result_dataset_new/"+dataset+"_FC"+FCNum+".mat", ...
            "powerList", "matDigit", "accDigit", "matAnalList", "accAnalList");
        emacList = 2*10.^(result.powerList/10) / band / 1000;
        accAnalList = result.accAnalList;
        plot(emacList, 1-accAnalList, "+-");
        set(gca, 'XScale', 'log');
        xlabel("E_{MAC} J/MAC");
        ylabel("Error Rate");
    end
end
legend("FC1", "FC2", "FC3", "FC4");