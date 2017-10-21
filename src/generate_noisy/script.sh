#!/bin/bash

directory="../../data/simulated/21oct/ground"

percentsFN=(0.15 0.25)
percentsFP=(0.0001)
percentsNA=(0.15)

files="$(find $directory -type f -name '*.SCnoNoise' | sort)"

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
				python2 noisy.py $f $fn $fp $na
			done
		done
	done
done