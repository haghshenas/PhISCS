#!/bin/bash

files="$(find ~/Desktop/result/6sep/z3-5/ -type f -name '*.txt' | sort)"
#files="$(find ./input/ground -type f -name '*.txt' | grep 'simID_1-n_50-m_50' | sort)"

for f in ${files}
do
	echo "Filename: "$f
	Rscript unique.R $f
done