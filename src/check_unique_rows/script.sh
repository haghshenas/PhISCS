#!/bin/bash

files="$(find ~/Desktop/full_new_simulations -type f -name '*.SCnoNoise' | sort)"
#files="$(find ./input/ground -type f -name '*.txt' | grep 'simID_1-n_50-m_50' | sort)"

for f in ${files}
do
	echo "Filename: "$f
	Rscript unique.R $f
done