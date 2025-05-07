%%  RF Receiver Modeling for LTE Reception
% This example demonstrates how to model and test an LTE RF receiver using
% LTE Toolbox(TM) and RF Blockset(TM).
% 
%

% Copyright 2009-2020 The MathWorks, Inc.

%% Model Description
% An LTE waveform
% is generated, filtered, transmitted through a propagation channel and fed
% into an RF Blockset receiver model. The RF model can be assembled using
% commercially available parts. EVM measurements are performed on the RF
% receiver output.
%
% This example is implemented using MATLAB(R) and Simulink(R), which
% interact at runtime. The functional partition is:
%
% <<../simrfV2_lte_rec_mat_sl.png>>
%
% The measurement testbench is implemented with a MATLAB script using an RF System object as the
% device under test (DUT). LTE frames are streamed
% between testbench and DUT.
%

%% Generate LTE Waveform
% In this section we generate the LTE waveform using the LTE Toolbox. We
% use the reference measurement channel (RMC) R.6 as defined in TS 36.101
% [ <#13 1> ]. This RMC specifies a 25 resource elements (REs) bandwidth,
% equivalent to 5 MHz. A 64 QAM modulation is used. All REs are allocated.
% Additionally, OCNG noise is enabled in unused REs.
%
% Only one frame is generated. This frame will then be repeated a number of
% times to perform the EVM measurements.
%

% Configuration TS 36.101 25 REs (5 MHz), 64-QAM, full allocation
rmc = lteRMCDL('R.6');
rmc.OCNGPDSCHEnable = 'On';

% Create eNodeB transmission with fixed PDSCH data
rng(2);                 % Fixed random seed (arbitrary)
data = randi([0 1], sum(rmc.PDSCH.TrBlkSizes),1);

% Generate 1 frame, to be repeated to simulate a total of N frames
[tx, ~, info] = lteRMCDLTool(rmc, data); % 1 frame

% Calculate the sampling period and the length of the frame.
SamplePeriod = 1/info.SamplingRate;
FrameLength = length(tx); 

%% Initialize Simulation Components 
% This section initializes some of the simulation components:
% 
% * Number of frames: this is the number of times the generated frame is
% repeated
% * Preallocate result vectors
%

% Number of simulation frames N>=1
N = 3;

% Preallocate vectors for results for N-1 frames
% EVM is not measured in the first frame to avoid transient effects
evmpeak = zeros(N,1);   % Preallocation for results
evmrms = zeros(N,1);    % Preallocation for results

%% Design RF Receiver
% The initial design of the RF receiver is done using the *RF Budget Analyzer* app.
% The receiver consists of a LNA, a direct conversion demodulator, and a
% final amplifier. All stages include noise and non-linearity.
%% 
load rfb;
%% 
% Type |show(rfb)| to display the initial design of the RF receiver in the *RF Budget Analyzer* app.
%
% <<../rfb_app.png>>
%


%% Create RF model for simulation
% From the RF budget object you can automatically create a model that can
% be used for circuit envelope simulation.

rfx = rfsystem(rfb); 
rfx.SampleTime = SamplePeriod;
open_system(rfx);

%% Extend the model of the RF receiver
% You can modify the model created in the previous section to include
% additional RF impairments and components. You can modify the created
% RF Blocket model as long as you do not change the input / output ports.
% This section loads a modified Simulink model that performs
% the following functions:
%
% * Channel model: includes free space path loss
% * RF receiver: includes direct conversion demodulator
% * ADC and DC offset cancellation
%
% You can open and inspect the modified model.

model = 'simrfV2_lte_receiver';
open_system(model);

%% Simulate Frames
% This section simulates the specified number of frames. 
% The RF system object simulates the Circuit Envelope model in
% |Accelerator| mode to decrease run time. After processing the first frame
% with the Simulink model, its state is preserved and automatically passed 
% to the successive frame.
%
% The output of the Simulink model is stored in the variable |rx|, which is
% available in the workspace. Any delays introduced to this signal are
% removed after performing synchronization. The EVM is measured on the
% resulting waveform.

load rfs;
EVMalg.EnablePlotting = 'Off';
cec.PilotAverage = 'TestEVM';

for n = 1:N 
    [I, Q]=rfs(tx);
    rx = complex(I,Q);

    % Synchronize to received waveform 
    if n==1
        Offset = lteDLFrameOffset(rmc,squeeze(rx),'TestEVM');
    end
    % Compute and display EVM measurements
    evmmeas = simrfV2_lte_receiver_evm_cal(rmc,cec,squeeze(rx),EVMalg);
    evmpeak(n) = evmmeas.Peak;
    evmrms(n) = evmmeas.RMS;
end

%% Visualize Measured EVM
% This section plots the measured peak and RMS EVM for each simulated
% frame.
%

hf(1) = figure;
plot((1:N), 100*evmpeak,'o-')
title('EVM peak %');
xlabel('Number of frames');
hf(2) = figure;
plot((1:N), 100*evmrms,'o-');
title('EVM RMS %');
xlabel('Number of frames');

%% Cleaning Up
% Close the Simulink model and remove the generated files.
release(rfs);
%close_system(rfs);
bdclose all;

%% Appendix
% This example uses the following helper function:
%
% * <matlab:edit('simrfV2_lte_receiver_evm_cal.m') simrfV2_lte_receiver_evm_cal.m>

%% Selected Bibliography
% # 3GPP TS 36.101 "User Equipment (UE) radio transmission and reception"


