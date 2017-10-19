#!/bin/bash


f="../../data/simulated/19oct/noisy/simID_1-n_100-m_50-fn_0.15-fp_0.0001-na_0.15-k_0.noisyMatrix"
#f="../../data/real/gawad.txt"

g="../../data/simulated/19oct/ground/simID_1-n_100-m_50-k_0.groundTruthMatrix"
o="/Users/Farid/Desktop/myresult"
fn="0.1"
fp="0.001"
fpW=$(echo "$(echo $fn/$fp|bc -l)/1"|bc)
z3="../../../z3-master/build/z3"

python2 main.py -f $f -n 1 -p $fpW -o $o -g $g -m 2 -z3path $z3
#python2 main.py -f $f -n 1 -p $fpW -o $o -m 2 -z3path $z3
