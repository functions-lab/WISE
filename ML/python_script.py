import subprocess
import concurrent
from concurrent.futures import wait
import logging
import os

NUM_OF_PROCESS = 40


def gen_str(size, bias, fc_method, second_c, ksize, n_chan):
    if 'size+1' == ksize:
        ksize = size + 1
    ksize_string = f'k{ksize}c{n_chan}'
    if second_c:
        ksize_string = ksize_string + '-' + ksize_string
    else:
        ksize_string = ksize_string + '-none'
    token_name = f'{fc_method}-{ksize_string}-b{bias}'
    ksize_str_w_comma = f'k{ksize},c{n_chan}'
    param_str = f'b{bias},{ksize_str_w_comma}'
    if second_c:
        param_str = f'{param_str},{ksize_str_w_comma}'
    ret = f'CUDA_VISIBLE_DEVICES={bias} python main.py --model {fc_method} --size {size} --token {token_name} --param {param_str}'
    return ret


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='python_script_log.log')
    
    hybrid_std = 'Hybrid-Std'
    hybrid_only = 'Hybrid'
    size_plus_1 = 'size+1'
    sizes = [256, 1024]
    biases = [0, 1]
    to_fc_method = [hybrid_std, hybrid_only]
    second_conv = [True, False]
    kernel_size = [3, 65, size_plus_1]
    n_channels = [64, 4, 1]
    count = 0
    futures = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_OF_PROCESS) as executor:
        for size in sizes:
            for bias in biases:
                for fc_method in to_fc_method:
                    for second_c in second_conv:
                        for ksize in kernel_size:
                            for n_chan in n_channels:
                                if count == 0:
                                    tmux_str = gen_str(size, bias, fc_method, second_c, ksize, n_chan)
                                    # print(tmux_str)
                                    count += 1
                                    futures.append(executor.submit(
                                            subprocess.run,
                                            [
                                                # "tmux", "new-session",
                                                # "-d",
                                                "screen", "-d", "-m",
                                                f'"{tmux_str}"', 
                                            ],
                                            capture_output=True, text=True, shell=False))
                                    print(' '.join([
                                                # "tmux", "new-session",
                                                # "-d",
                                                "screen", "-d", "-m",
                                                f'"{tmux_str}"', 
                                            ]))
                                break
        print(count)
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                data = future.result().stdout
                err = future.result().stderr
                logging.error(err)
                print(err)
            except Exception as e:
                logging.error('getting future.result() errored out:\n' + e)
        wait(futures)
        