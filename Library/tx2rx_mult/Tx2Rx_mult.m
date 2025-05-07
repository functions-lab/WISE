function [packetRx, snr, cfo] = Tx2Rx_mult(packetList_1, packetList_2, rxNum, sampleRate, shrink, freq, param)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("Tx2Rx_mult"));

    CheckSaturation(packetList_1);
    CheckSaturation(packetList_2);
    [txNum_1, packetLen] = size(packetList_1);
    [txNum_2, ~] = size(packetList_2);
    padLen = max([20e-3*sampleRate round(0.1*packetLen)]);
    capNum = 3;
    noiseNum = 1000;
    zadoffSet = [139 839]*shrink; % ascent
    zadoffNum = length(zadoffSet);

    bufferPath = thisPath+"Buffer/";
%     bufferPath = "/dev/shm/Buffer/";
    if ~exist(bufferPath, "dir")
        mkdir(bufferPath)
    else
        delete(bufferPath+"*");
    end

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
    waveLen = 2*padLen + headLen + packetLen;

    fileTxStr = "";
    freqTxStr = "";
    gainTxStr = "";
    for txIdx_1 = 1: txNum_1
        waveTemp = [padTx zadoff_1 packetList_1(txIdx_1, :) padTx];
        Wave2File(bufferPath+"Tx_1_"+txIdx_1+".bin", waveTemp);
        fileTxStr = fileTxStr + bufferPath+"Tx_1_"+txIdx_1+".bin,";
        freqTxStr = freqTxStr + param.carrierTx(1)+",";
        gainTxStr = gainTxStr + param.gainTx(1)+",";
    end
    deviceNum = count(param.deviceTx(1), ',')+1;
    for txIdx_1 = txNum_1+1: deviceNum*2
        fileTxStr = fileTxStr + ".,";
        freqTxStr = freqTxStr + ".,";
        gainTxStr = gainTxStr + ".,";
    end
    for txIdx_2 = 1: txNum_2
        waveTemp = [padTx zadoff_2 packetList_2(txIdx_2, :) padTx];
        Wave2File(bufferPath+"Tx_2_"+txIdx_2+".bin", waveTemp);
        fileTxStr = fileTxStr + bufferPath+"Tx_2_"+txIdx_2+".bin,";
        freqTxStr = freqTxStr + param.carrierTx(2)+",";
        gainTxStr = gainTxStr + param.gainTx(2)+",";
    end
    deviceTx = param.deviceTx(1) + "," + param.deviceTx(2);

    fileRxStr = "";
    for rxIdx = 1: rxNum
        fileRxStr = fileRxStr + bufferPath+"Rx_"+rxIdx+".bin,";
    end
    freqRxStr = string(param.carrierRx+freq);
    gainRxStr = string(param.gainRx);
    deviceRx = param.deviceRx;
    
    while 1
        try
            system("bash "+thisPath+"Tx2Rx_mult.sh " + ...
                max(1.0, (capNum+1)*waveLen/sampleRate)+" "+...
                deviceTx+" "+sampleRate+" "+param.clockTx+" "+...
                fileTxStr+" "+freqTxStr+" "+gainTxStr+" "+...
                deviceRx+" "+sampleRate/shrink+" "+param.clockRx+" "+...
                fileRxStr+" "+freqRxStr+" "+gainRxStr);

            waveRx = NaN(rxNum, capNum*round(waveLen/shrink));
            offsetZadoffList = NaN(1, rxNum);
            offsetPacketList = NaN(1, rxNum);
            isSuccess = 1;
            for rxIdx = 1: rxNum
                waveTemp = File2Wave(bufferPath+"/Rx_"+rxIdx+".bin");
                waveTemp = waveTemp(end-capNum*round(waveLen/shrink)+1: end);
                waveRx(rxIdx, :) = waveTemp;

                [offsetList, corrList] = ZadoffDetection( ...
                    waveTemp(1: round(waveLen/shrink)).', ...
                    round(zadoffSet(end)/shrink), round(zadoffSet(end)/shrink), 0.7);
                [offsetListAfter, ~] = ZadoffDetection( ...
                    waveTemp(round(waveLen/shrink): 2*round(waveLen/shrink)).', ...
                    round(zadoffSet(end)/shrink), round(zadoffSet(end)/shrink), 0.7);
                if (length(offsetList)<1)||(length(offsetListAfter)<1)
                    isSuccess = 0;
                    break;
                end
                [~, offsetIdx] = max(corrList);
                offsetZadoffTemp = offsetList(offsetIdx)-3*sum(round(zadoffSet(1: end-1)/shrink));
                offsetPacketTemp = offsetZadoffTemp + round(headLen/shrink);
                if offsetZadoffTemp <= 0
                    isSuccess = 0;
                    break;
                end
                offsetZadoffList(rxIdx) = offsetZadoffTemp;
                offsetPacketList(rxIdx) = offsetPacketTemp;
            end
            if ~isSuccess
                continue;
            end
        catch
            continue;
        end
        break;
    end

    packetRx = NaN(rxNum, round(packetLen/shrink));
    cfo = NaN(1, rxNum);
    snr = NaN(1, rxNum);
    figure(99);
    for rxIdx = 1: rxNum
        waveTemp = waveRx(rxIdx, :);

        pfOffset = comm.PhaseFrequencyOffset( ...
            'SampleRate', sampleRate/shrink, ...
            'FrequencyOffsetSource', 'Input port');
        cfoSet = NaN(1, zadoffNum);
        offset = offsetZadoffList(rxIdx);
        for zadoffIdx = 1: zadoffNum
            zadoffLen = round(zadoffSet(zadoffIdx)/shrink);
    
            zadoff_1 = waveTemp(offset+(1: zadoffLen));
            zadoff_2 = waveTemp(offset+zadoffLen+(1: zadoffLen)) * exp(+1i*2*pi*freq*zadoffLen/sampleRate*shrink);
            cfoSet(zadoffIdx) = -sampleRate/shrink/zadoffLen*angle(sum(zadoff_1.*conj(zadoff_2)))/2/pi;
            offset = offset + 3*zadoffLen;
    
            waveTemp(offsetZadoffList(rxIdx)+1: offsetZadoffList(rxIdx)+round(headLen/shrink)) = ...
                pfOffset(waveTemp(offsetZadoffList(rxIdx)+1: offsetZadoffList(rxIdx)+round(headLen/shrink)).', -mean(cfoSet(zadoffIdx))).';
        end
        cfo(rxIdx) = sum(cfoSet);
        pfOffset = comm.PhaseFrequencyOffset( ...
            'SampleRate', sampleRate/shrink, ...
            'FrequencyOffsetSource', 'Input port');
        packetTemp = waveTemp(offsetPacketList(rxIdx)+1: offsetPacketList(rxIdx)+round(packetLen/shrink));
        packetRx(rxIdx, :) = pfOffset(packetTemp.', -cfo(rxIdx)).';

        noiseList = zeros(1, noiseNum);
        for noiseIdx = 1: noiseNum
            startIdx = round(length(waveTemp)/noiseNum*(noiseIdx-1)) + 1;
            endIdx = round(length(waveTemp)/noiseNum*(noiseIdx-1)) + round(4e-6*sampleRate/shrink);
            noiseSym = waveTemp(startIdx: endIdx);
            noise = GetEnergy(noiseSym);
            noiseList(noiseIdx) = noise;
        end
        noise = prctile(noiseList, 10);
        signal = GetEnergy(packetTemp) - noise;
        snr(rxIdx) = 10 * log10(signal/noise);

        subplot(rxNum, 1, rxIdx);
        plot(1: capNum*round(waveLen/shrink), 20*log10(abs(waveTemp)+1e-10));
        xline(offsetZadoffList(rxIdx));
        xline(offsetPacketList(rxIdx));
        xline(offsetPacketList(rxIdx)+round(packetLen/shrink));
        ylim([-100 0]);
        title("SNR: "+snr(rxIdx)+"dB CFO:"+cfo(rxIdx)+"Hz");
    end
%     saveas(gcf, bufferPath+"detection.png");
end