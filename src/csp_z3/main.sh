#!/bin/bash


f="../../data/simulated/17oct/noisy/simID_1-n_10-m_50-fn_0.1-fp_0.001-na_0-k_0.noisyMatrix"
g="../../data/simulated/17oct/ground/simID_1-n_10-m_50-k_0.groundTruthMatrix"
o="/Users/Farid/Desktop/res"
fn="0.1"
fp="0.001"
fpW=$(echo "$(echo $fn/$fp|bc -l)/1"|bc)

python2 main.py -f $f -n 1 -p $fpW -o $o -g $g -m 2
