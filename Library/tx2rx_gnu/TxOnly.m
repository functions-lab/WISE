function [] = TxOnly(packet_1, packet_2, param)
    time = 1000;
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("TxOnly"));

    Wave2File(thisPath+"Buffer/Tx_1.bin", packet_1);
    Wave2File(thisPath+"Buffer/Tx_2.bin", packet_2);

    system("bash "+thisPath+"TxOnly.sh " + ...
        param.sampleRate+" "+time+" "+...
        param.deviceTx+" "+...
        param.carrierTx(1)+" "+thisPath+"Buffer/Tx_1.bin "+param.gainTx(1)+" "+...
        param.carrierTx(2)+" "+thisPath+"Buffer/Tx_2.bin "+param.gainTx(2));
end