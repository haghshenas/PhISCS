#!/bin/bash

directory="../../data/simulated/17oct/ground"

f="../../data/simulated/17oct/noisy/simID_1-n_10-m_50-fn_0.1-fp_0.001-na_0-k_0.noisyMatrix"
o="../../"

simID=(1..10)
Ns=(10 20 50)
Ms=(50)
percentsFN=(0.05 0.1 0.15 0.2 0.25 0.3)
percentsFP=(0.001 0.0001 0.00001)
percentsNA=(0)
percentsK=(0)

files="$(find $directory -type f -name '*.txt' | sort)"

for id in ${files}
do
	echo "simID: "$id
	for n in ${Ns}
	do
		echo "N: "$id
		for m in ${Ms}
		do
			echo "M: "$id
			for fn in ${percentsFN[@]}
			do
				echo "FN: "$fn
				for fp in ${percentsFP[@]}
				do
					echo "FP: "$fp
					python2 main.py $f $id $n $m $fn $fp $o
					#for na in ${percentsNA[@]}
					#do
					#	echo "NA: "$na
					#	for k in ${percentsK[@]}
					#	do
					#		echo "K: "$k
							
					#	done
					#done
				done
			done
		done
	done
done
