function [outputList] = LayerFC_analyzeRx(waveOutput, span, shape, param)
    symNum = shape.symNum;
    inputLen = shape.inputLen;
    outputLen = shape.outputLen;

    if param.cpRate >= 0
        cpRate = param.cpRate;
    else
        cpRate = 2/outputLen; % Only include the first lobe of sinc function
    end
    
    cpLen = round(outputLen*cpRate)*span;
    batchLen = outputLen*span + cpLen;
    offset = floor((span-1)/2*outputLen);

    outputList = zeros(symNum, outputLen);
    for symIdx = 1: symNum
        startIdx = (symIdx-1) * batchLen + 1;
        endIdx = symIdx * batchLen;
        outputAll = DecodeWave(waveOutput(startIdx: endIdx), cpLen);
        outputList(symIdx, :) = outputAll(offset+1: offset+outputLen);
    end
    outputList = fliplr(outputList);
    if (mod(inputLen, 2)==0)&&(mod(outputLen, 2)==1)
        disp("Warning: Even Input Size and Odd Output Size are NOT Recommended!");
        outputList = circshift(outputList, 1, 2);
    end
end

function [output] = DecodeWave(wave, cpLen)
    waveMid = wave(round(cpLen/2)+1: end+round(cpLen/2)-cpLen);
    output = circshift(fft(waveMid), ceil(length(waveMid)/2));
end