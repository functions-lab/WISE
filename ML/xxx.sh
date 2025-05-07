#!/bin/bash

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c64-k3c64-b0 --param b0,k3,c64,k3,c64' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c4-k3c4-b0 --param b0,k3,c4,k3,c4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c1-k3c1-b0 --param b0,k3,c1,k3,c1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c64-k5c64-b0 --param b0,k5,c64,k5,c64' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c4-k5c4-b0 --param b0,k5,c4,k5,c4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c1-k5c1-b0 --param b0,k5,c1,k5,c1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c64-k7c64-b0 --param b0,k7,c64,k7,c64' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c4-k7c4-b0 --param b0,k7,c4,k7,c4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c1-k7c1-b0 --param b0,k7,c1,k7,c1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c64-none-b0 --param b0,k3,c64' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c4-none-b0 --param b0,k3,c4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c1-none-b0 --param b0,k3,c1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c64-none-b0 --param b0,k5,c64' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c4-none-b0 --param b0,k5,c4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c1-none-b0 --param b0,k5,c1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c64-none-b0 --param b0,k7,c64' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c4-none-b0 --param b0,k7,c4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=0 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c1-none-b0 --param b0,k7,c1' &



# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c64-k3c64-b1 --param b1,k3,c64,k3,c64' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c4-k3c4-b1 --param b1,k3,c4,k3,c4' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c1-k3c1-b1 --param b1,k3,c1,k3,c1' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c64-k5c64-b1 --param b1,k5,c64,k5,c64' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c4-k5c4-b1 --param b1,k5,c4,k5,c4' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c1-k5c1-b1 --param b1,k5,c1,k5,c1' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c64-k7c64-b1 --param b1,k7,c64,k7,c64' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c4-k7c4-b1 --param b1,k7,c4,k7,c4' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c1-k7c1-b1 --param b1,k7,c1,k7,c1' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c64-none-b1 --param b1,k3,c64' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c4-none-b1 --param b1,k3,c4' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k3c1-none-b1 --param b1,k3,c1' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c64-none-b1 --param b1,k5,c64' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c4-none-b1 --param b1,k5,c4' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k5c1-none-b1 --param b1,k5,c1' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c64-none-b1 --param b1,k7,c64' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c4-none-b1 --param b1,k7,c4' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --model Hybrid-Std --size 1024 --token flatten-k7c1-none-b1 --param b1,k7,c1' &
