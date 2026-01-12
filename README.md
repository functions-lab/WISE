# Disaggregated machine learning via in-physics computing at radio frequency

## Concept Introduction

<img width="2540" height="1690" alt="image" src="https://github.com/user-attachments/assets/66e14c6f-8acf-438c-8b07-c0556c6640fe" />

**The WISE architecture enables disaggregated model access and energy-efficient machine learning (ML) for multiple clients in wireless edge networks.**

**a.** A central radio broadcasts frequency-encoded model weights, **W**, onto a radio-frequency (RF) signal at the carrier frequency $F_w$, which is precoded to **V** to mitigate distortion introduced during propagation over the wireless channel, **H**.

**b.** Each client equipped with WISE encodes the inference request **x** at the carrier frequency $F_x$, and performs local ML inference for **y** at the carrier frequency $F_y$. Each fully connected (FC) layer in the ML model, corresponding to a matrix-vector multiplication (MVM), is realized using a passive computing mixer.

**c.** Illustration of the in-physics MVM computation during frequency down-conversion with frequency-encoded **W**, **x** and **y**.


## Code Usage

In this repository, you can find two components of code in `WISE`:

a) the complex-valued machine learning model training and testing in digital [here](./ML/).

b) the analog computing simulations with randomized inputs and weights [here](./Hybrid/).

(The experimental codes are also included in this repo, but the instructions are upon request)

## Reference

If you find our work useful in your research, please consider citing our [paper](https://www.science.org/doi/10.1126/sciadv.adz0817):

```console
@article{gao2026disaggregated,
  title = {Disaggregated deep learning via in-physics computing at radio frequency},
  author = {Gao, Zhihui and Vadlamani, Sri Krishna and Sulimany, Kfir and Englund, Dirk and Chen, Tingjun},
  journal = {Science Advances},
  year = {2026},
  publisher = {American Association for the Advancement of Science},
}
```

If you have any further questions, please feel free to contact us at :D

zhihui.gao@duke.edu
