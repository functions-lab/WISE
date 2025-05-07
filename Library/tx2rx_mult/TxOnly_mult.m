function [] = TxOnly_mult(packetList_1, packetList_2, param)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("TxOnly_mult"));

    [txNum_1, ~] = size(packetList_1);
    [txNum_2, ~] = size(packetList_2);

    bufferPath = thisPath+"Buffer/";
%     bufferPath = "/dev/shm/Buffer/";
    if ~exist(bufferPath, "dir")
        mkdir(bufferPath)
    else
        delete(bufferPath+"*");
    end

    fileTxStr = "";
    freqTxStr = "";
    gainTxStr = "";
    for txIdx_1 = 1: txNum_1
        Wave2File(bufferPath+"Tx_1_"+txIdx_1+".bin", packetList_1(txIdx_1, :));
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
        Wave2File(bufferPath+"Tx_2_"+txIdx_2+".bin", packetList_2(txIdx_2, :));
        fileTxStr = fileTxStr + bufferPath+"Tx_2_"+txIdx_2+".bin,";
        freqTxStr = freqTxStr + param.carrierTx(2)+",";
        gainTxStr = gainTxStr + param.gainTx(2)+",";
    end
    deviceTx = param.deviceTx(1) + "," + param.deviceTx(2);

    system("bash "+thisPath+"TxOnly_mult.sh " + ...
        deviceTx+" "+param.sampleRate+" "+param.clockTx+" "+...
        fileTxStr+" "+freqTxStr+" "+gainTxStr);
end