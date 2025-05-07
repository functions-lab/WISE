#!/bin/bash

time=$1

deviceTx=$2
rateTx=$3
clockTx=$4
carrier_1=$5
file_1=$6
gain_1=$7
carrier_2=$8
file_2=$9
gain_2=${10}

deviceRx=${11}
rateRx=${12}
clockRx=${13}
carrierRx=${14}
fileRx=${15}
gainRx=${16}

python "$(dirname -- "${BASH_SOURCE[0]}")"/USRP.py \
    --addr $deviceTx --rate $rateTx --time 100 --sync 0 --clock $clockTx \
    --fileTX_1 $file_1 --freqTX_1 $carrier_1 --gainTX_1 $gain_1 \
    --fileTX_2 $file_2 --freqTX_2 $carrier_2 --gainTX_2 $gain_2 &
pid=$!
sleep 4s
python "$(dirname -- "${BASH_SOURCE[0]}")"/USRP.py \
    --addr $deviceRx --rate $rateRx --time $time --sync 0 --clock $clockRx \
    --fileRX_1 $fileRx --freqRX_1 $carrierRx --gainRX_1 $gainRx
kill -9 $pid
