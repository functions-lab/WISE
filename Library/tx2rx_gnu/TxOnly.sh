#!/bin/bash

rate=$1
time=$2

deviceTx=$3
carrier_1=$4
file_1=$5
gain_1=$6
carrier_2=$7
file_2=$8
gain_2=$9

python "$(dirname -- "${BASH_SOURCE[0]}")"/USRP.py \
    --addr $deviceTx --rate $rate --time $time \
    --fileTX_1 $file_1 --freqTX_1 $carrier_1 --gainTX_1 $gain_1 \
    --fileTX_2 $file_2 --freqTX_2 $carrier_2 --gainTX_2 $gain_2

