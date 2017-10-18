#!/bin/bash

directory="../../data/simulated/17oct/ground"

percentsFN=(0.05 0.1 0.15 0.2 0.25 0.3)
percentsFP=(0.001 0.0001 0.00001)
percentsNA=(0)
percentsK=(0)

files="$(find $directory -type f -name '*.txt' | sort)"

for f in ${files}
do
	echo "Filename: "$f
	for fn in ${percentsFN[@]}
	do
		echo "FN: "$fn
		for fp in ${percentsFP[@]}
		do
			echo "FP: "$fp
			for na in ${percentsNA[@]}
			do
				echo "NA: "$na
				for k in ${percentsK[@]}
				do
					echo "K: "$k
					python2 noisy.py $f $fn $fp $na $k
				done
			done
		done
	done
done