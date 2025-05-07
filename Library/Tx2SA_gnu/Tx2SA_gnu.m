function [] = Tx2SA_gnu(packet_1, packet_2, carrier, param, token)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("Tx2SA_gnu"));

    CheckSaturation(packet_1);
    CheckSaturation(packet_2);

    if ~exist(thisPath+"Buffer", "dir")
        mkdir(thisPath+"Buffer")
    else
        delete(thisPath+"Buffer/*");
    end

    Wave2File(thisPath+"Buffer/Tx_1.bin", packet_1);
    Wave2File(thisPath+"Buffer/Tx_2.bin", packet_2);

    system("bash "+thisPath+"Tx2SA_gnu.sh " + ...
        carrier+" "+param.sampleRate+" "+token+" "+...
        param.sampleRate+" "+param.deviceTx+" "+...
        param.carrier_1+" "+thisPath+"Buffer/Tx_1.bin "+param.gain_1+" "+...
        param.carrier_2+" "+thisPath+"Buffer/Tx_2.bin "+param.gain_2+" "+...
        thisPath+"Buffer/zero.bin");
end