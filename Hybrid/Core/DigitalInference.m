function [output] = DigitalInference(input, CONVList, window, FCList, act)
    data = reshape(input.', 1, []);
    
    for CONVIdx = 1: length(CONVList)
        CONV = CONVList{CONVIdx};
        data = conv(CONV, data);
        data = Activation(data, act);
    end

    if window > 0
        featNum = length(data);
        if mod(featNum - window, 2) == 1
            offset = (featNum - window - 1) / 2;
        else
            offset = (featNum - window) / 2;
        end
        data = data(offset+1: offset+window);
    end

    for FCIdx = 1: length(FCList)-1
        FC = FCList{FCIdx};
        data = data * FC.';
        data = Activation(data, act);
    end
    data = data * FCList{end}.';

    if act == "relu"
        output = data;
    else
        output = abs(data);
    end
end

