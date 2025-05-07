#!/bin/bash

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h1000,h1000" --token Ryan1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h256,h256" --token Ryan2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h100,h100" --token Ryan3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 14 --type zadoff --model Hybrid --act zadoff --param "h64,h32" --token Ryan4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 14 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan5' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 7 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan6' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 7 --type zadoff --model Hybrid --act zadoff --param "h16,h16" --token Ryan7' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 7 --type zadoff --model Hybrid --act zadoff --param "" --token Ryan8' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h1000,h1000" --token Ryan1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h256,h256" --token Ryan2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h100,h100" --token Ryan3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 14 --type zadoff --model Hybrid --act zadoff --param "h64,h32" --token Ryan4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 14 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan5' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 7 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan6' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 7 --type zadoff --model Hybrid --act zadoff --param "h16,h16" --token Ryan7' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data FMNIST --size 7 --type zadoff --model Hybrid --act zadoff --param "" --token Ryan8' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "h1000,h1000" --token Ryan1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "h256,h256" --token Ryan2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "h100,h100" --token Ryan3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 16 --type zadoff --model Hybrid --act zadoff --param "h64,h32" --token Ryan4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 16 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan5' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 8 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan6' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 8 --type zadoff --model Hybrid --act zadoff --param "h16,h16" --token Ryan7' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data SVHN --size 8 --type zadoff --model Hybrid --act zadoff --param "" --token Ryan8' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "h1000,h1000" --token Ryan1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "h256,h256" --token Ryan2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "h100,h100" --token Ryan3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 16 --type zadoff --model Hybrid --act zadoff --param "h64,h32" --token Ryan4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 16 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan5' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 8 --type zadoff --model Hybrid --act zadoff --param "h32,h16" --token Ryan6' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 8 --type zadoff --model Hybrid --act zadoff --param "h16,h16" --token Ryan7' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 8 --type zadoff --model Hybrid --act zadoff --param "" --token Ryan8' &

# tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h1000,h1000" --token Ryan1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h256,h256" --token Ryan2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h100,h100" --token Ryan3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 2000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h64,h32" --token Ryan4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data Audio --size 2000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h32,h16" --token Ryan5' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data Audio --size 1000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h32,h16" --token Ryan6' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data Audio --size 1000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h16,h16" --token Ryan7' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=3 python main.py --data Audio --size 1000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "" --token Ryan8' &
