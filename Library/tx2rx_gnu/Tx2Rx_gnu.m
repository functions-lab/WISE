function [packetRx, snr, cfo] = Tx2Rx_gnu(packet_1, packet_2, sampleRate, shrink, freq, param)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("Tx2Rx_gnu"));

    CheckSaturation(packet_1);
    CheckSaturation(packet_2);

    padLen = max([20e-3*sampleRate round(0.1*length(packet_1)) round(0.1*length(packet_2))]);
    capNum = 3;
    noiseNum = 1000;
    zadoffSet = [139 839]*shrink; % ascent
    bufferPath = thisPath+"Buffer/";
%     bufferPath = "/dev/shm/Buffer/";
    if ~exist(bufferPath, "dir")
        mkdir(bufferPath)
    else
        delete(bufferPath+"*");
    end

    packetLen = size(packet_1, 2);
    zadoffNum = length(zadoffSet);

    zadoff_1 = [];
    zadoff_2 = [];
    for zadoffIdx = 1: zadoffNum
        zadoffLen = zadoffSet(zadoffIdx);
%         zadoff = repmat(myZadoff(zadoffLen)/(shrink^0.125), [1 2]);
        zadoff = repmat(exp(1i*2*pi*rand(1, zadoffLen)), [1 2]);
        zadoff_1 = [zadoff_1 0.5*zadoff zeros(1, zadoffLen)]; %#ok<AGROW> 
        zadoff = repmat(exp(1i*2*pi*rand(1, zadoffLen)), [1 2]);
        zadoff_2 = [zadoff_2 0.5*zadoff zeros(1, zadoffLen)]; %#ok<AGROW> 
    end
    headLen = size(zadoff_1, 2);

    padTx = zeros(1, padLen);

    wave_1 = [padTx zadoff_1 packet_1 padTx];
    wave_2 = [padTx zadoff_2 packet_2 padTx];
    Wave2File(bufferPath+"Tx_1.bin", wave_1);
    Wave2File(bufferPath+"Tx_2.bin", wave_2);
    waveLen = length(wave_1);
    
    while 1
        try
            system("bash "+thisPath+"Tx2Rx_gnu.sh " + ...
                max(1.0, (capNum+1)*waveLen/sampleRate)+" "+...
                param.deviceTx+" "+sampleRate+" "+param.clockTx+" "+...
                param.carrierTx(1)+" "+bufferPath+"Tx_1.bin "+param.gainTx(1)+" "+...
                param.carrierTx(2)+" "+bufferPath+"Tx_2.bin "+param.gainTx(2)+" "+...
                param.deviceRx+" "+sampleRate/shrink+" "+param.clockRx+" "+...
                (param.carrierRx+freq)+" "+bufferPath+"/Rx.bin "+param.gainRx);
            waveRx = File2Wave(bufferPath+"/Rx.bin");
            waveRx = waveRx(end-capNum*round(waveLen/shrink)+1: end);

            [offsetList, corrList] = ZadoffDetection( ...
                waveRx(1: round(waveLen/shrink)).', ...
                round(zadoffSet(end)/shrink), round(zadoffSet(end)/shrink), 0.8);
            [offsetListAfter, ~] = ZadoffDetection( ...
                waveRx(round(waveLen/shrink): 2*round(waveLen/shrink)).', ...
                round(zadoffSet(end)/shrink), round(zadoffSet(end)/shrink), 0.8);
            if (length(offsetList)<1)||(length(offsetListAfter)<1)
                continue;
            end
            [~, offsetIdx] = max(corrList);
            offsetZadoff = offsetList(offsetIdx)-3*sum(round(zadoffSet(1: end-1)/shrink));
            offsetPacket = offsetZadoff + round(headLen/shrink);
            if offsetZadoff <= 0
                continue;
            end
        catch
            continue;
        end
        break;
    end

    pfOffset = comm.PhaseFrequencyOffset( ...
        'SampleRate', sampleRate/shrink, ...
        'FrequencyOffsetSource', 'Input port');
    cfoSet = zeros(1, zadoffNum);
    offset = offsetZadoff;
    for zadoffIdx = 1: zadoffNum
        zadoffLen = round(zadoffSet(zadoffIdx)/shrink);

        zadoff_1 = waveRx(offset+(1: zadoffLen));
        zadoff_2 = waveRx(offset+zadoffLen+(1: zadoffLen)) * exp(+1i*2*pi*freq*zadoffLen/sampleRate*shrink);
        cfoSet(zadoffIdx) = -sampleRate/shrink/zadoffLen*angle(sum(zadoff_1.*conj(zadoff_2)))/2/pi;
        offset = offset + 3*zadoffLen;

        waveRx(offsetZadoff+1: offsetZadoff+round(headLen/shrink)) = ...
            pfOffset(waveRx(offsetZadoff+1: offsetZadoff+round(headLen/shrink)).', -mean(cfoSet(zadoffIdx))).';
    end
    cfo = sum(cfoSet);
    pfOffset = comm.PhaseFrequencyOffset( ...
        'SampleRate', sampleRate/shrink, ...
        'FrequencyOffsetSource', 'Input port');
    packetRx = waveRx(offsetPacket+1: offsetPacket+round(packetLen/shrink));
    packetRx = pfOffset(packetRx.', -cfo).';

    noiseList = zeros(1, noiseNum);
    for noiseIdx = 1: noiseNum
        startIdx = round(length(waveRx)/noiseNum*(noiseIdx-1)) + 1;
        endIdx = round(length(waveRx)/noiseNum*(noiseIdx-1)) + round(4e-6*sampleRate/shrink);
        noiseSym = waveRx(startIdx: endIdx);
        noise = GetEnergy(noiseSym);
        noiseList(noiseIdx) = noise;
    end
    noise = prctile(noiseList, 10);
    signal = GetEnergy(packetRx) - noise;
    snr = 10 * log10(signal/noise);

    figure(99);
    plot(1: capNum*round(waveLen/shrink), 20*log10(abs(waveRx)+1e-10));
    xline(offsetZadoff);
    xline(offsetPacket);
    xline(offsetPacket+round(packetLen/shrink));
    ylim([-100 0]);
    title("SNR: "+snr+"dB CFO:"+cfo+"Hz");
%     saveas(gcf, bufferPath+"detection.png");
end