#!/bin/bash

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type real --model Hybrid-Std --act relu --param "h1000,h300,h100" --token FC4_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type real --model Hybrid-Std --act relu --param "h300,h100" --token FC3_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type real --model Hybrid-Std --act relu --param "h100" --token FC2_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type real --model Hybrid-Std --act relu --param "" --token FC1_fix' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type real --model Hybrid-Std --act relu --param "h1000,h300,h100" --token FC4_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type real --model Hybrid-Std --act relu --param "h300,h100" --token FC3_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type real --model Hybrid-Std --act relu --param "h100" --token FC2_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type real --model Hybrid-Std --act relu --param "" --token FC1_fix' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type real --model Hybrid-Std --act relu --param "h1000,h300,h100" --token FC4_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type real --model Hybrid-Std --act relu --param "h300,h100" --token FC3_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type real --model Hybrid-Std --act relu --param "h100" --token FC2_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type real --model Hybrid-Std --act relu --param "" --token FC1_fix' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type real --model Hybrid-Std --act relu --param "h1000,h300,h100" --token FC4_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type real --model Hybrid-Std --act relu --param "h300,h100" --token FC3_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type real --model Hybrid-Std --act relu --param "h100" --token FC2_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type real --model Hybrid-Std --act relu --param "" --token FC1_fix' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type real --model Hybrid-Std --act relu --param "h1000,h300,h100" --token FC4_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type real --model Hybrid-Std --act relu --param "h300,h100" --token FC3_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type real --model Hybrid-Std --act relu --param "h100" --token FC2_fix' &
# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type real --model Hybrid-Std --act relu --param "" --token FC1_fix' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type stft-abs-200 --model Hybrid-Std --act relu --param "h1000,h300,h100" --token FC4_stft-abs' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type stft-abs-200 --model Hybrid-Std --act relu --param "h300,h100" --token FC3_stft-abs' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type stft-abs-200 --model Hybrid-Std --act relu --param "h100" --token FC2_stft-abs' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 24000 --dilate 6 --type stft-abs-200 --model Hybrid-Std --act relu --param "" --token FC1_stft-abs' &
