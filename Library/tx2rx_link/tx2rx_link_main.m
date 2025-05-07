% function [packetRx] = tx2rx_link() % tx2rx_link(packet_1, packet_2, sampleRate, shrink, freq, param)

clear;
clc;
close all;
rng(3);

sampleRate = 100e6;
packet_1 = randn(1, 10).'+1i*randn(1, 10)';
packet_2 = randn(1, 10).'+1i*randn(1, 10)';

packetLen = length(packet_1);
timeAxis = (1: packetLen).' / sampleRate;

simPacket_1.time = timeAxis;
simPacket_1.signals.values = packet_1 * 1e-2;
simPacket_2.time = timeAxis;
simPacket_2.signals.values = packet_2 * 1e-2;

temperature = 290;
analog = 10e9;
simParam.sampleRate = 1/analog;
simParam.time = timeAxis(end);
simParam.temperature = temperature;
simParam.noiseIn = 0; % rf.physconst('Boltzmann')*temperature;
simParam.noiseOut = rf.physconst('Boltzmann')*temperature;
simParam.carrier_1 = 1.5e9;
simParam.carrier_2 = 1.0e9;
simParam.carrierRx = 0.5e9;

result = sim('tx2rx_link_simulink.slx');

timeTemp = result.simPacket_1.Time;
test = result.simPacket_1.Data;
figure(2);
plot(timeTemp, real(test), timeTemp, imag(test));

timeTemp = result.simPacket_2.Time;
test = result.simPacket_2.Data;
figure(3);
plot(timeTemp, real(test), timeTemp, imag(test));

timeTemp = result.simPacketRx.Time;
packetRx = result.simPacketRx.Data;
figure(1);
plot(timeTemp, real(packetRx), timeTemp, imag(packetRx));
% end