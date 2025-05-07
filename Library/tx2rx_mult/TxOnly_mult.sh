#!/bin/bash

deviceTx=$1
rateTx=$2
clockTx=$3
fileTx=$4
carrierTx=$5
gainTx=$6

python "$(dirname -- "${BASH_SOURCE[0]}")"/USRP_mult.py \
    --addr $deviceTx --rate $rateTx --time -1 --sync 1 --clock $clockTx \
    --fileTx $fileTx --freqTx $carrierTx --gainTx $gainTx