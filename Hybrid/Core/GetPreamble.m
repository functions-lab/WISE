function [input, weight] = GetPreamble(inputLen, outputLen)
    R_input = 25;
    R_output = 29;

    inputPhase = zeros(1, inputLen);
    if mod(inputLen, 2) == 1
        for inputIdx = 1: inputLen
            inputPhase(inputIdx) = R_input*inputIdx*(inputIdx-1)/inputLen;
        end
    else
        for inputIdx = 1: inputLen-1
            inputPhase(inputIdx) = R_input*inputIdx*(inputIdx-1)/(inputLen-1);
        end
        inputPhase(end) = inputPhase(1);
    end
    outputPhase = zeros(1, outputLen);
    if mod(outputLen, 2) == 1
        for outputIdx = 1: outputLen
            outputPhase(outputIdx) = R_output*outputIdx*(outputIdx-1)/outputLen;
        end
    else
        for outputIdx = 1: outputLen-1
            outputPhase(outputIdx) = R_output*outputIdx*(outputIdx-1)/(outputLen-1);
        end
        outputPhase(end) = outputPhase(1);
    end

    input = exp(-1i*pi*inputPhase);
    weight = zeros(inputLen, outputLen);
    for inputIdx = 1: inputLen
        for outputIdx = 1: outputLen
            weight(inputIdx, outputIdx) = ...
                1/exp(-1i*pi*(-inputPhase(inputIdx)+outputPhase(outputIdx)));
        end
    end
end