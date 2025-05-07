clear;
clc;
close all;
rng(0);

%%

moduList = ["BPSK", "QPSK", "16QAM", "64QAM"];
dataSize = 1024;
modelList = ["flatten", "sum"];
biasList = ["b0", "b1"];
convList_1 = ["k3c64", "k5c64", "k7c64", "k3c4", "k5c4", "k7c4", "k3c1", "k5c1", "k7c1"];
convList_2 = ["x", "none"];

%%

for modelIdx = 1: length(modelList)
    model = modelList(modelIdx);

    for biasIdx = 1: length(biasList)
        bias = biasList(biasIdx);

        accMat = NaN(length(convList_2), length(convList_1));
        epochMat = NaN(length(convList_2), length(convList_1));
        for convIdx_1 = 1: length(convList_1)
            conv_1 = convList_1(convIdx_1);

            for convIdx_2 = 1: length(convList_2)
                if convList_2(convIdx_2) == "x"
                    conv_2 = conv_1;
                else
                    conv_2 = convList_2(convIdx_2);
                end

                token = model + "-" + conv_1 + "-" + conv_2 + "-" + bias;
                resultPath = "./Result/DeepSig_size"+dataSize+"_"+token+"/";
                if ~exist(resultPath, "dir")
                    disp(resultPath);
                    continue;
                end
            
                result = load(resultPath+"model_accMax.mat");
                accMat(convIdx_2, convIdx_1) = result.accTest(end, end);

                result = load(resultPath+"model_last.mat");
                epochMat(convIdx_2, convIdx_1) = size(result.lossTest, 1);

                % heatmap(moduList, moduList, squeeze(result.matTest(end, :, :)));
                % xlabel("Actual");
                % ylabel("Predicted");
                % title(token+" acc: "+result.accTest(end));
            end
        end
        figure(1);
        % hold on;
        subplot(length(modelList)*length(biasList), 1, (modelIdx-1)*length(biasList)+biasIdx);
        heatmap(convList_1, convList_2, accMat);
        title(model + " " + bias);

        figure(2);
        % hold on;
        subplot(length(modelList)*length(biasList), 1, (modelIdx-1)*length(biasList)+biasIdx);
        heatmap(convList_1, convList_2, epochMat);
        title(model + " " + bias);
    end
end