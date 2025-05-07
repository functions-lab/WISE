function [packetRx, snr, cfo] = Tx2Rx_gnu_new(packetList, sampleRate, param)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("Tx2Rx_gnu_new"));

    [packetNum, packetLen] = size(packetList);
    for packetIdx = 1: packetNum
        CheckSaturation(packetList(packetIdx, :));
    end

    padLen = max([10e-3*sampleRate round(0.5*packetLen)]);
    capNum = 2;
    noiseNum = 1000;
    zadoffSet = [139 839]; % ascent
    if ~exist(thisPath+"Buffer", "dir")
        mkdir(thisPath+"Buffer")
    else
        delete(thisPath+"Buffer/*");
    end
    zadoffNum = length(zadoffSet);

    zadoff = [];
    for zadoffIdx = 1: zadoffNum
        zadoffLen = zadoffSet(zadoffIdx);
        zadoff = [zadoff 0.5*repmat(zadoffChuSeq(25, zadoffLen).', [1 2]) zeros(1, zadoffLen)]; %#ok<AGROW>
    end
    headLen = length(zadoff);

    padTx = zeros(1, padLen);

    waveLen = 2*padLen + headLen + packetLen;
    command = "python "+thisPath+"USRP_new.py "+...
        "--addr "+param.device+" --rate "+sampleRate+" --time "+max(1.0, capNum*waveLen/sampleRate)+" "+...
        "--fileRX_4 "+thisPath+"Buffer/Rx.bin --freqRX_4 "+param.carrierRx+" --gainRX_4 "+param.gainRx+" ";
    for packetIdx = 1: packetNum
        fileName = thisPath+"Buffer/Tx_"+packetIdx+".bin";
        Wave2File(fileName, [padTx zadoff packetList(packetIdx, :) padTx]);
        command = command + ...
            "--fileTX_" + packetIdx + " " + fileName + " " + ...
            "--freqTX_" + packetIdx + " " + param.carrierTx(packetIdx) + " " + ...
            "--gainTX_" + packetIdx + " " + param.gainTx(packetIdx)+" ";
    end
    
    while 1
        try
            system(command);
            waveRx = File2Wave(thisPath+"Buffer/Rx.bin");
            waveRx = waveRx(end-capNum*waveLen+1: end);

            [offsetList, corrList] = ZadoffDetection( ...
                waveRx(1: waveLen).', zadoffSet(end), zadoffSet(end), 0.8);
            if length(offsetList) < 2
                continue;
            end
            [~, offsetIdx] = max(corrList);
            offsetZadoff = offsetList(offsetIdx)-3*sum(zadoffSet(1: end-1));
            offsetPacket = offsetZadoff + headLen;
            if offsetZadoff <= 0
                continue;
            end
        catch
            continue;
        end
        break;
    end

    figure(11);
    plot(1: capNum*waveLen, 20*log10(abs(waveRx)+1e-10));
    xline(offsetZadoff);
    xline(offsetPacket);
    xline(offsetPacket+packetLen);
    ylim([-100 0]);
    saveas(gcf, thisPath+"Buffer/detection.png");

    pfOffset = comm.PhaseFrequencyOffset( ...
        'SampleRate', sampleRate, ...
        'FrequencyOffsetSource', 'Input port');
    cfoSet = zeros(1, zadoffNum);
    offset = offsetZadoff;
    for zadoffIdx = 1: zadoffNum
        zadoffLen = zadoffSet(zadoffIdx);

        zadoff_1 = waveRx(offset+(1: zadoffLen));
        zadoff_2 = waveRx(offset+zadoffLen+(1: zadoffLen));
        cfoSet(zadoffIdx) = -sampleRate/zadoffLen*angle(sum(zadoff_1.*conj(zadoff_2)))/2/pi;
        offset = offset + 3*zadoffLen;

        waveRx(offsetZadoff+1: offsetZadoff+headLen) = pfOffset(waveRx(offsetZadoff+1: offsetZadoff+headLen).', -mean(cfoSet(zadoffIdx))).';
    end
    cfo = sum(cfoSet);
    pfOffset = comm.PhaseFrequencyOffset( ...
        'SampleRate', sampleRate, ...
        'FrequencyOffsetSource', 'Input port');
%     waveRxBoth(offsetPacket: offsetPacket+packetLen, 1) = pfOffset(waveRxBoth(offsetPacket: offsetPacket+packetLen, 1), -cfo);
%     waveRxBoth(offsetPacket: offsetPacket+packetLen, 2) = pfOffset(waveRxBoth(offsetPacket: offsetPacket+packetLen, 2), -cfo);
    packetRx = waveRx(offsetPacket+1: offsetPacket+packetLen);
    packetRx = pfOffset(packetRx.', -cfo).';

    noiseList = zeros(1, noiseNum);
    for noiseIdx = 1: noiseNum
        startIdx = round(length(waveRx)/noiseNum*(noiseIdx-1)) + 1;
        endIdx = round(length(waveRx)/noiseNum*(noiseIdx-1)) + round(4e-6*sampleRate);
        noiseSym = waveRx(startIdx: endIdx);
        noise = GetEnergy(noiseSym);
        noiseList(noiseIdx) = noise;
    end
    noise = prctile(noiseList, 10);
    signal = GetEnergy(packetRx) - noise;
    snr = 10 * log10(signal/noise);
end