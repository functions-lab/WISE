function [valueMaxList] = PickMax(keyList, valueList, num)
    valueMaxList = zeros(1, num);
    for idx = 1: num
        [~, idxMax] = max(keyList);
        valueMaxList(idx) = valueList(idxMax);

        keyList(idxMax) = [];
        valueList(idxMax) = [];
    end
end