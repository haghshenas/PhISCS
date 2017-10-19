#!/bin/bash

directory="../../data/simulated/19oct/noisy"
o="./result"
z3="../../../z3-master/build/z3"

percentsFN=(0.15 0.25)
percentsFP=(0.0001)
percentsNA=(0.15)
percentsK=(0)

files="$(find $directory -type f -name '*.noisyMatrix' | sort)"

for f in ${files}
do
	echo "File: "$f
	for fn in ${percentsFN[@]}
	do
		echo "FN: "$fn
		for fp in ${percentsFP[@]}
		do
			echo "FP: "$fp
			for na in ${percentsNA[@]}
			do	
				fpW=$(echo "$(echo $fn/$fp|bc -l)/1"|bc)
				g=$(echo $f | sed "s/noisy/ground/g")
				g=$(echo $g | sed "s/-fn_${fn}//g")
				g=$(echo $g | sed "s/-fp_${fp}//g")
				g=$(echo $g | sed "s/-na_${na}//g")
				g=$(echo $g | sed "s/groundMatrix/groundTruthMatrix/g")
				python main.py -f $f -n 1 -p $fpW -o $o -g $g -z3path $z3
			done
			
		done
	done
done
