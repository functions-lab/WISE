function [outputList, waveTime] = AnalogInference(inputList, CONVList, window, FCList, act, method, param)
    if param.transMode == "exp"
        batchInOutProd = param.batchInOutProd;
        if param.decMode == "freq"
            batchOutProd = +inf;
        else
            batchOutProd = param.batchOutProd;
        end
    else
        batchInOutProd = -1;
        batchOutProd = -1;
    end
    userNum = param.userNum;

    dataNum = size(inputList, 1);
    dataList = repmat(reshape(permute(inputList, [1 3 2]), 1, dataNum, []), [userNum 1 1]);
    waveTime = 0;
    
%     for CONVIdx = 1: length(CONVList)
%         CONV = CONVList{CONVIdx};
%         [dataList, waveTimeTemp] = LayerConv1D(dataList, CONV.', param);
%         waveTime = waveTime + waveTimeTemp;
% %         dataList = ActSelf(dataList, param);
%         dataList = Activation(dataList, act);
%     end
% 
%     if window > 0
%         featNum = size(dataList, 2);
%         if mod(featNum - window, 2) == 1
%             offset = (featNum - window - 1) / 2;
%         else
%             offset = (featNum - window) / 2;
%         end
%         dataList = dataList(:, offset+1: offset+window);
%     end

    for FCIdx = 1: length(FCList)
        FC = FCList{FCIdx}.';
        [inputSize, outputSize] = size(FC);
        if(batchInOutProd<0)||(batchOutProd<0)
            batchNum = 100;
        else
            batchNum = max(min(floor(batchInOutProd/inputSize/outputSize), floor(batchOutProd/outputSize)), 1);
        end

        dataTempList = zeros(userNum, dataNum, outputSize);
        for batchIdx = 1: ceil(dataNum/batchNum)
            startIdx = (batchIdx-1) * batchNum + 1;
            endIdx = min(batchIdx * batchNum, dataNum);
            disp("Progress: FC["+FCIdx+"/"+length(FCList)+"], batch["+batchIdx+"/"+ceil(dataNum/batchNum)+"]");
        
            data = dataList(:, startIdx: endIdx, :);
            [dataTemp, ~, waveTimeTemp] = LayerFC(data, FC, method, param);
            dataTemp = reshape(dataTemp, [userNum (endIdx-startIdx+1) outputSize]);
            dataTempList(:, startIdx: endIdx, :) = dataTemp;
            waveTime = waveTime + waveTimeTemp;
        end
        dataList = dataTempList;

        if FCIdx < length(FCList)
            dataList = reshape(dataList, userNum*dataNum, []);
            dataList = Activation(dataList, act);
            dataList = reshape(dataList, userNum, dataNum, []);
        end
    end
    outputList = abs(dataList);
end

