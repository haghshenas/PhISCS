#!/bin/bash

directory='./simulations'
percentsFN=(0.05 0.10 0.15 0.25)
percentsFP=(0.0001)
percentsNA=(0.15)
files="$(find $directory -type f -name '*.SCnoNoise' | sort)"
for f in ${files}
do
	for fn in ${percentsFN[@]}
	do
		for fp in ${percentsFP[@]}
		do
			for na in ${percentsNA[@]}
			do
				inFile=${f}-fn_${fn}-fp_${fp}-na_${na}
				echo $inFile
				python2 noisy.py $f $fn $fp $na
			done
		done
	done
done
