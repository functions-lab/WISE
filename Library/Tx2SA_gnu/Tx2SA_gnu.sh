#!/bin/bash

carrier=${1}
band=${2}
token=${3}

rate=${4}
deviceTx=${5}
carrier_1=${6}
file_1=${7}
gain_1=${8}
carrier_2=${9}
file_2=${10}
gain_2=${11}
file_zero=${12}

deviceRx=${13}
carrierRx=${11}
fileRx=${12}
gainRx=${13}

python "$(dirname -- "${BASH_SOURCE[0]}")"/USRP.py \
    --addr $deviceTx --rate $rate --time 100 \
    --fileTX_1 $file_1 --freqTX_1 $carrier_1 --gainTX_1 $gain_1 \
    --fileTX_2 $file_2 --freqTX_2 $carrier_2 --gainTX_2 $gain_2 &
pid=$!
sleep 3s
python "$(dirname -- "${BASH_SOURCE[0]}")"/SA.py \
    --csv $token --device USBDISK --carrier $carrier --band $band
sleep 1s
kill -9 $pid
sleep 1s