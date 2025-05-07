function [freqList, powerList] = CSV2Spec(fileName)
    file = readtable(fileName);
    freqList = file(4: end-1, "x_DATAFreq");
    freqList = freqList{:, :};
    powerList = file(4: end-1, "SAAverage");
    powerList = powerList{:, :};
end

