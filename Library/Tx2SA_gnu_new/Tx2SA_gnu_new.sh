#!/bin/bash

carrier=${1}
band=${2}
token=${3}
command=${4}

eval "$command &"
pid=$!
sleep 3s
python "$(dirname -- "${BASH_SOURCE[0]}")"/SA.py \
    --csv $token --device USBDISK --carrier $carrier --band $band
sleep 1s
kill -9 $pid
sleep 5s