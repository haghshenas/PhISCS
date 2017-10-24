#!/bin/bash


#f="../../data/simulated/17oct/noisy/simID_1-n_10-m_50-fn_0.1-fp_0.001-na_0-k_0.noisyMatrix"
f="../../data/simulated/21oct/noisy/simNo_1-n_100-m_40-s_4-minVAF_0.05-cov_2000-k_0-fn_0.15-fp_0.0001-na_0.15.SCnoisy"
#f="../../data/real/gawad.txt"

b="../../data/simulated/21oct/ground/simNo_1-n_100-m_40-s_4-minVAF_0.05-cov_2000-k_0.bulk"
o="/Users/Farid/Desktop/myresult"
fn="0.15"
fp="0.0001"
fpW=$(echo "$(echo $fn/$fp|bc -l)/1"|bc)

python2 main.py -f $f -n 1 -p $fpW -o $o -b $b -m 2 -e 0.1
