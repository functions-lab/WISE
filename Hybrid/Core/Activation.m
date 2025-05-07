function [output] = Activation(input, act)
    [batchNum, featNum] = size(input);
    if act == "conv"
        output = NaN(batchNum, featNum*2-1);
        for batchIdx = 1: batchNum
            output(batchIdx, :) = conv(input(batchIdx, :), input(batchIdx, :));
        end
    elseif act == "zadoff"
        zadoff = myZadoff(featNum);
        output = NaN(batchNum, featNum);
        for batchIdx = 1: batchNum
            output(batchIdx, :) = squeeze(abs(input(batchIdx, :))) .* zadoff;
        end
    elseif act == "relu"
        output = max(input, 0);
    else
        disp("Warning: Activation Function NOT Found!");
    end
end

