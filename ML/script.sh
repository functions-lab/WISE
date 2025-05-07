#!/bin/bash

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h1000,h300,h100" --token FC4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h300,h100" --token FC3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h100" --token FC2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data MNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "" --token FC1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h1000,h300,h100" --token FC4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h300,h100" --token FC3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "h100" --token FC2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data FMNIST --size 28 --type zadoff --model Hybrid --act zadoff --param "" --token FC1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "h1000,h300,h100" --token FC4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "h300,h100" --token FC3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "h100" --token FC2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data SVHN --size 32 --type zadoff --model Hybrid --act zadoff --param "" --token FC1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "h1000,h300,h100" --token FC4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "h300,h100" --token FC3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "h100" --token FC2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data CIFAR-10 --size 32 --type zadoff --model Hybrid --act zadoff --param "" --token FC1' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h1000,h300,h100" --token FC4' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h300,h100" --token FC3' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "h100" --token FC2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --data Audio --size 4000 --type stft-zadoff-200 --model Hybrid --act zadoff --param "" --token FC1' &