#!/bin/bash

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python train.py --input 4000' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python train.py --input 1000' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python train.py --input 784' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python train.py --input 300' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python train.py --input 100' &
