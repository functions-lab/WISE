function [] = CheckSaturation(packet)
    threshold = 1;
    packetLin = reshape(packet, 1, []);
    ratio = sum(abs(packetLin)>threshold)/length(packetLin);
    if ratio > 0
        disp("Warning: Packet Saturated for "+ratio*100+"%");
    end
end

