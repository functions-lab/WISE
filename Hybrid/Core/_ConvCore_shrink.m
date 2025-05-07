function [output] = ConvCore_shrink(input_1, input_2, ratio, param)
    [symNum_1, inputLen_1] = size(input_1);
    [symNum_2, inputLen_2] = size(input_2);
    if symNum_1 ~= symNum_2
        disp("Warning: Input Symbol Number NOT Matched!");
    end
    symNum = min(symNum_1, symNum_2);

    convert = param.convert;
    cpRate = param.cpRate;
    outputLen = inputLen_1 + inputLen_2 - 1;
    cpLen = round(outputLen*cpRate);
    symLen = outputLen + cpLen;

    wave_1 = symNum*symLen;
    wave_2 = symNum*symLen;
    for symIdx = 1: symNum
        startIdx = (symIdx-1) * symLen + 1;
        endIdx = symIdx * symLen;
        wave_1(startIdx: endIdx) = EncodeWave(input_1(symIdx, :), outputLen, cpLen, 0);
        if convert == "up"
            wave_2(startIdx: endIdx) = EncodeWave(input_2(symIdx, :), outputLen, cpLen, 0);
        else
            wave_2(startIdx: endIdx) = EncodeWave(input_2(symIdx, :), outputLen, cpLen, 1);
        end
    end
    wave_1 = 0.2 * wave_1 ./ sqrt(mean(abs(wave_1).^2));
    wave_2 = 0.2 * wave_2 ./ sqrt(mean(abs(wave_2).^2));

%     wave = wave_1 .* wave_2 * outputLen;
    [wave, ~, ~] = Tx2Rx_gnu(wave_1, wave_2, param.sampleRate, ratio, param);

    output = zeros(symNum, outputLen);
    for symIdx = 1: symNum
        startIdx = (symIdx-1) * symLen + 1;
        endIdx = symIdx * symLen;
        output(symIdx, :) = DecodeWave(wave(startIdx: endIdx), round(inputLen_1/2)+round(inputLen_2/2), cpLen);
    end
end

function [wave] = EncodeWave(input, waveLen, cpLen, reverse)
    spec = zeros(1, waveLen);
    spec(1: length(input)) = input;
    spec = circshift(spec, -round(length(input)/2));
    if reverse
        spec = conj(flip(circshift(spec, -1)));
    end
    waveSing = ifft(spec);
    waveMult = repmat(waveSing, 1, ceil(cpLen/waveLen/2));
    wave = [waveMult(end-round(cpLen/2)+1: end) waveSing waveMult(1: cpLen - round(cpLen/2))];
end

function [output] = DecodeWave(wave, offset, cpLen)
    waveMid = wave(round(cpLen/2)+1: end+round(cpLen/2)-cpLen);
    output = circshift(fft(waveMid), offset);
end