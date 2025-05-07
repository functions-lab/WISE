function [outputList] = LayerFC_analyzeRx_full(waveOutput, freqOffset, shape, param)
    symNum = shape.symNum;
    inputLen = shape.inputLen;
    outputLen = shape.outputLen;

    if param.cpRate >= 0
        cpRate = param.cpRate;
    else
        cpRate = 2/outputLen; % Only include the first lobe of sinc function
    end
    
    cpLen = inputLen*round(outputLen*cpRate);
    batchLen = inputLen * outputLen + cpLen;

    outputList = zeros(symNum, outputLen);
    outputOffset = round((inputLen-1)*outputLen/2);
    for symIdx = 1: symNum
        startIdx = (symIdx-1) * batchLen + 1;
        endIdx = symIdx * batchLen;
        outputAll = DecodeWave(waveOutput(startIdx: endIdx), cpLen);
        outputList(symIdx, :) = outputAll(outputOffset+2*freqOffset+1: outputOffset+2*freqOffset+outputLen);
    end
    outputList = fliplr(outputList);
end

function [output] = DecodeWave(wave, cpLen)
    waveMid = wave(round(cpLen/2)+1: end+round(cpLen/2)-cpLen);
    output = circshift(fft(waveMid), ceil(length(waveMid)/2)+1);
end