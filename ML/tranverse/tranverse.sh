tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106 --token cross-log_conv_106_1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106 --token cross-log_conv_106_2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106 --token cross-log_conv_106_3' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106,401 --token cross-log_conv_106,401_1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106,401 --token cross-log_conv_106,401_2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106,401 --token cross-log_conv_106,401_3' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106,401,1001 --token cross-log_conv_106,401,1001_1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106,401,1001 --token cross-log_conv_106,401,1001_2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 106,401,1001 --token cross-log_conv_106,401,1001_3' &



tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206 --token cross-log_conv_206_1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206 --token cross-log_conv_206_2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206 --token cross-log_conv_206_3' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206,1201 --token cross-log_conv_206,1201_1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206,1201 --token cross-log_conv_206,1201_2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206,1201 --token cross-log_conv_206,1201_3' &

tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206,1201,6001 --token cross-log_conv_206,1201,6001_1' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206,1201,6001 --token cross-log_conv_206,1201,6001_2' &
tmux new-session -d 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 206,1201,6001 --token cross-log_conv_206,1201,6001_3' &



tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406 --token cross-log_conv_406_1' &
tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406 --token cross-log_conv_406_2' &
tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406 --token cross-log_conv_406_3' &

tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406,2801 --token cross-log_conv_406,2801_1' &
tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406,2801 --token cross-log_conv_406,2801_2' &
tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406,2801 --token cross-log_conv_406,2801_3' &

tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406,2801,12001 --token cross-log_conv_406,2801,12001_1' &
tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406,2801,12001 --token cross-log_conv_406,2801,12001_2' &
tmux new-session 'CUDA_VISIBLE_DEVICES=1 python main.py --hidden 406,2801,12001 --token cross-log_conv_406,2801,12001_3' &
