function [outputList] = LayerFC_analyzeRx(waveOutput, span, shape, param)
    symNum = shape.symNum;
    inputLen = shape.inputLen;
    outputLen = shape.outputLen;
    decMode = param.decMode;

    if param.cpRate >= 0
        cpRate = param.cpRate;
    else
        cpRate = 2/outputLen; % Only include the first lobe of sinc function
    end
    padRate = param.padRate;
    
    cpLen = round(outputLen*cpRate)*span;
    padLen = span*round(outputLen*padRate);
    batchLen = outputLen*span + cpLen + padLen;
    offset = floor((span-1)/2*outputLen);

    outputList = zeros(symNum, outputLen);
    for symIdx = 1: symNum
        startIdx = (symIdx-1) * batchLen + 1;
        endIdx = symIdx * batchLen;

        waveCP = waveOutput(startIdx: endIdx);
        waveSing = RemoveCP(waveCP, cpLen, padLen);
        if decMode == "time"
            outputAll = waveSing; % DecodeWaveTrans(waveSing);
        else
            outputAll = DecodeWave(waveSing);
        end
        outputList(symIdx, :) = outputAll(offset+1: offset+outputLen);
    end
    outputList = fliplr(outputList);
    if (mod(inputLen, 2)==0)&&(mod(outputLen, 2)==1)
        disp("Warning: Even Input Size and Odd Output Size are NOT Recommended!");
        outputList = circshift(outputList, 1, 2);
    end
end

function [output] = DecodeWave(wave)
    output = circshift(fft(wave), ceil(length(wave)/2));
end

function [output] = DecodeWaveTrans(wave)
    fftSize= length(wave);
    transform = circshift(dftmtx(fftSize), ceil(fftSize/2), 2);
    output = wave * transform;
end

function [waveOut] = RemoveCP(waveIn, cpLen, padLen)
    if cpLen == 0 % for acceleration
        wavePad = waveIn;
    else
        wavePad = waveIn(round(cpLen/2)+1: end+round(cpLen/2)-cpLen);
    end
    if padLen == 0 % for acceleration
        waveOut = wavePad;
    else
        padLeft = floor(padLen/2);
        padRight = padLen - padLeft;
        waveOut = wavePad(padLeft+1: end-padRight);
    end
end