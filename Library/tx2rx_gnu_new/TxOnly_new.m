function [] = TxOnly_new(packetList, sampleRate, param)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("TxOnly_new"));

    packetNum = size(packetList, 1);

    command = "python "+thisPath+"USRP_new.py --addr "+param.deviceTx+" --rate "+sampleRate+" --time -1 ";
    for packetIdx = 1: packetNum
        fileName = thisPath+"Buffer/Tx_"+packetIdx+".bin";
        Wave2File(fileName, packetList(packetIdx, :));
        command = command + ...
            "--fileTX_" + packetIdx + " " + fileName + " " + ...
            "--freqTX_" + packetIdx + " " + param.carrierTx(packetIdx) + " " + ...
            "--gainTX_" + packetIdx + " " + param.gainTx(packetIdx)+" ";
    end

    system(command);
end