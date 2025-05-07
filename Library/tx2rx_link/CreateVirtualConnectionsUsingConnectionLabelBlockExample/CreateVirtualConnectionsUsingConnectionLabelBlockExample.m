clear;
clc;
close all;

x = [3 1];
y = sim("docexconnectionlabel.slx");
aa = y.simout.time;
bb = y.simout.Data;
