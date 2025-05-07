function [param] = GetParam()
    % Transmission Mode
    % [fast] for my simulation
    % [link] for Simulink based simulation (not recommended)
    % [exp] for experiment on URSPs
    param.transMode = "exp";
    % [freq] for conducting IFFT seperately
    % [time] for combining IFFT into the weight matrix
    param.encMode = "time";
    % [freq] for conducting IFFT seperately
    % [time] for combining IFFT into the weight matrix
    % [inner] for splitting into inner-products
    % [split-X] for splitting into sub-MVM with output size of X
    param.decMode = "split-1";
    param.sampleRate = 100e6;

    % Simulation and Simulink
    param.analog = 6e9;
    param.impedance = 50;

    param.boltzmann = physconst("Boltzmann");
    param.temperature = 300;
    % Fast
    param.powerRF = -50; % [dBm]
    param.powerLO = -50; % [dBm]
    param.insertion = 11.97;
    param.noisefigure = 13.32;
    % Easy
    param.powerRF = -37; % [dBm]
    param.noisefigure = 28;


    % Experiment
    param.delay = 0; % I/Q samples for weight wave
    param.calib = [];
    param.precode = "weight"; % input or weight
    param.cpRate = -1; % -1 for automatic, only include the first lobe of sinc function
    param.padRate = 0.333; % 0;
    if param.transMode == "exp"
        param.subMax = 1000000;
        param.subMin = 1;
        param.guardDC = 1e-5;
        % Used for FC Full
        param.guardInput = 0.05;
        % Used for FC Shrink
        param.guardOutput = 0.1;
    else
        param.subMax = +inf;
        param.subMin = 1;
        param.guardInput = 1e-10;
        param.guardOutput = 1e-10;
        param.guardDC = 0;
    end
    % Settings for normalization:
    % [positive] for whole waveform normalization, e.g., one-time test
    % [negative] for per-symbol normalization, e.g., ML inference
    % [NaN] for no normalization, e.g., calibration
    param.inputNorm = 0.2;
    param.weightNorm = 0.2;
    param.userNum = 1;
    param.attenList = [0];
    param.atten = NaN;
    % Empirical batch size limits
    param.batchInOutProd = 100000000;
    param.batchOutProd = 100000; % NOT effective for param.decMode = "freq";
    param.autoEdge = 500;

    % USRP Control
    param.deviceTx = ["192.168.70.3" "192.168.70.6"];
    param.clockTx = 200e6;
    param.deviceRx = "192.168.70.9"; % None for skipping USRP Rx
    param.clockRx = 200e6;

    param.carrierTx = [1.2e9 0.9e9];
    param.convert = "down"; % "down" or "up"
    if param.convert == "up"
        param.carrierRx = param.carrierTx(1) + param.carrierTx(2);
    elseif param.convert == "down"
        param.carrierRx = abs(param.carrierTx(1) - param.carrierTx(2));
    end

%     param.gainTx = [15.5 11.5]; % Best linearity with ATT: 0+0 -> 20dB
    param.gainTx = [9 19]; % Low RF power with ATT: 35+0 -> 0dB
    param.gainRx = 20;
end