function [] = Tx2SA_gnu_new(packetList, channelList, carrier, param, token)
    thisPath = mfilename("fullpath");
    thisPath = thisPath(1: end-strlength("Tx2SA_gnu_new"));

    [packetNum, ~] = size(packetList);
    for packetIdx = 1: packetNum
        CheckSaturation(packetList(packetIdx, :));
    end

    if ~exist(thisPath+"Buffer", "dir")
        mkdir(thisPath+"Buffer")
    else
        delete(thisPath+"Buffer/*");
    end

    command = "python "+thisPath+"USRP_new.py "+...
        "--addr "+param.device+" --rate "+param.sampleRate+" --time 100 ";
    for packetIdx = 1: packetNum
        fileName = thisPath+"Buffer/Tx_"+packetIdx+".bin";
        Wave2File(fileName, packetList(packetIdx, :));
        command = command + ...
            "--fileTX_" + channelList(packetIdx) + " " + fileName + " " + ...
            "--freqTX_" + channelList(packetIdx) + " " + param.carrierTx(packetIdx) + " " + ...
            "--gainTX_" + channelList(packetIdx) + " " + param.gainTx(packetIdx)+" ";
    end

    system("bash "+thisPath+"Tx2SA_gnu_new.sh " + ...
        carrier+" "+param.sampleRate+" "+token+" '"+command+"'");
end