function [packetRx, snr, cfo] = Tx2Rx_gnu(packet_1, packet_2, sampleRate, param)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("Tx2Rx_gnu"));

    CheckSaturation(packet_1);
    CheckSaturation(packet_2);

    padLen = max([10e-3*sampleRate round(0.5*length(packet_1)) round(0.5*length(packet_2))]);
    capNum = 2;
    noiseNum = 1000;
    zadoffSet = [139 839]; % ascent
    if ~exist(thisPath+"Buffer", "dir")
        mkdir(thisPath+"Buffer")
    else
        delete(thisPath+"Buffer/*");
    end

    packetLen = size(packet_1, 2);
    zadoffNum = length(zadoffSet);

    zadoff_1 = [];
    zadoff_2 = [];
    for zadoffIdx = 1: zadoffNum
        zadoffLen = zadoffSet(zadoffIdx);
        zadoff = repmat(zadoffChuSeq(25, zadoffLen).', [1 2]);
        zadoff_1 = [zadoff_1 ...
            0.5*zadoff zeros(1, zadoffLen) 0.5*ones(1, 2*zadoffLen) zeros(1, zadoffLen)]; %#ok<AGROW> 
        zadoff_2 = [zadoff_2 ...
            0.5*ones(1, 2*zadoffLen) zeros(1, zadoffLen) 0.5*zadoff zeros(1, zadoffLen)]; %#ok<AGROW> 
    end
    headLen = size(zadoff_1, 2);

    padTx = zeros(1, padLen);

    wave_1 = [padTx zadoff_1 packet_1 padTx];
    wave_2 = [padTx zadoff_2 packet_2 padTx];
    Wave2File(thisPath+"Buffer/Tx_1.bin", wave_1);
    Wave2File(thisPath+"Buffer/Tx_2.bin", wave_2);
    waveLen = length(wave_1);
    
    while 1
        try
            system("bash "+thisPath+"Tx2Rx_gnu.sh " + ...
                sampleRate+" "+max(1.0, capNum*waveLen/sampleRate)+" "+...
                param.deviceTx+" "+...
                param.carrier_1+" "+thisPath+"Buffer/Tx_1.bin "+param.gain_1+" "+...
                param.carrier_2+" "+thisPath+"Buffer/Tx_2.bin "+param.gain_2+" "+...
                param.deviceRx+" "+param.carrierRx+" "+thisPath+"Buffer/Rx.bin "+param.gainRx);
            waveRx = File2Wave(thisPath+"Buffer/Rx.bin");
            waveRx = waveRx(end-capNum*waveLen+1: end);

            [offsetList, corrList] = ZadoffDetection( ...
                waveRx(1: waveLen).', zadoffSet(end), zadoffSet(end), 0.8);
            if length(offsetList) < 2
                continue;
            end
            offsetMaxList = sort(PickMax(corrList, offsetList, 2));
            offset_1 = offsetMaxList(1);
            offset_2 = offsetMaxList(2);
            offsetZadoff = round((offset_1+offset_2-3*zadoffSet(end))/2)-6*sum(zadoffSet(1: end-1));
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
    cfoSet = zeros(2, zadoffNum);
    offset = offsetZadoff;
    for zadoffIdx = 1: zadoffNum
        zadoffLen = zadoffSet(zadoffIdx);

        zadoff_1 = waveRx(offset+(1: zadoffLen));
        zadoff_2 = waveRx(offset+zadoffLen+(1: zadoffLen));
        cfoSet(zadoffIdx, 1) = -sampleRate/zadoffLen*angle(sum(zadoff_1.*conj(zadoff_2)))/2/pi;
        offset = offset + 3*zadoffLen;

        zadoff_1 = waveRx(offset+(1: zadoffLen));
        zadoff_2 = waveRx(offset+zadoffLen+(1: zadoffLen));
        cfoSet(zadoffIdx, 2) = -sampleRate/zadoffLen*angle(sum(zadoff_1.*conj(zadoff_2)))/2/pi;
        offset = offset + 3*zadoffLen;

        waveRx(offsetZadoff+1: offsetZadoff+headLen) = pfOffset(waveRx(offsetZadoff+1: offsetZadoff+headLen).', -mean(cfoSet(zadoffIdx), 2)).';
    end
    cfo = sum(mean(cfoSet, 2));
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