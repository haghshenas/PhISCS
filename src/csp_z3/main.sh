#!/bin/bash

directory="../../data/simulated/17oct/ground"

f="../../data/simulated/17oct/noisy/simID_1-n_10-m_50-fn_0.1-fp_0.001-na_0-k_0.noisyMatrix"
o="../../"

python2 main.py $f 1 10 50 0.1 0.001 $o
