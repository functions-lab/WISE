function [packetRx, SNR] = tx2rx_link(packet_1, packet_2, sampleRate, shrink, freqOffset, param)
    packetLen = min(length(packet_1), length(packet_2));
    padLen = round(0.2 * packetLen);
    padding = zeros(1, padLen);
    timeAxis = (1: (packetLen+2*padLen)).' / sampleRate;
    
    simParam.packet_1.time = timeAxis;
    simParam.packet_1.signals.values = [padding packet_1 padding].';
    simParam.packet_2.time = timeAxis;
    simParam.packet_2.signals.values = [padding packet_2 padding].';
    simParam.sampleRate = sampleRate;
    simParam.analog = param.analog;
    simParam.time = timeAxis(end);
    simParam.temperature = param.temperature;
    simParam.noiseIn = 0; % rf.physconst('Boltzmann')*param.temperature;
    simParam.noiseOut = rf.physconst('Boltzmann')*param.temperature;
    simParam.carrier_1 = param.carrierTx(1);
    simParam.carrier_2 = param.carrierTx(2);
    simParam.carrierRx = param.carrierRx; % + freq;
    simParam.passLow = param.carrierRx+freqOffset-sampleRate/shrink/2;
    simParam.passHigh = param.carrierRx+freqOffset+sampleRate/shrink/2;
    assignin("base", "simParam", simParam);
    
    tic;
    result = sim('tx2rx_link_simulink.slx');
    toc;
    
%     figure(1);
%     timeTemp = result.wave_1.Time;
%     wave_1 = result.wave_1.Data;
%     subplot(4, 1, 1);
%     plot(timeTemp, real(wave_1), timeTemp, imag(wave_1), timeTemp, abs(wave_1));
%     title("Input Waveform 1");
%     timeTemp = result.wave_2.Time;
%     wave_2 = result.wave_2.Data;
%     subplot(4, 1, 2);
%     plot(timeTemp, real(wave_2), timeTemp, imag(wave_2), timeTemp, abs(wave_2));
%     title("Input Waveform 1");
%     subplot(4, 1, 3);
%     plot((1: packetLen)/sampleRate, real(packet_1.*packet_2), ...
%         (1: packetLen)/sampleRate, imag(packet_1.*packet_2), ...
%         (1: packetLen)/sampleRate, abs(packet_1.*packet_2));
%     title("Multiplication");
%     timeTemp = result.waveRx.Time;
%     waveRx = result.waveRx.Data;
%     subplot(4, 1, 4);
%     plot(timeTemp, real(waveRx), timeTemp, imag(waveRx), timeTemp, abs(waveRx));
%     title("Output Waveform");
% 
%     figure(2);
%     plot((1: packetLen)/sampleRate, abs(packet_1.*packet_2), timeTemp, abs(waveRx));

    waveRx = result.waveRx.Data;
    packetRx = zeros(1, round(packetLen/shrink));
    for packetIdx = 1: round(packetLen/shrink)
        timeNow = packetIdx / sampleRate * shrink + padLen / sampleRate;
        packetRx(packetIdx) = waveRx(round(timeNow*param.analog)) * exp(1i*2*pi*freqOffset*timeNow);
    end

    noise_1 = GetEnergy(waveRx(1: padLen));
    noise_2 = GetEnergy(waveRx(end-padLen+1: end));
    noise = (noise_1 + noise_2) / 2;
    signal = GetEnergy(packetRx) - noise;
    SNR = 10 * log10(signal/noise);
end