#!/bin/bash

directory="../../data/simulated/19oct"
o="./result"
z3="../../../z3-master/build/z3"

n="100"
m="50"
percentsFN=(0.15 0.25)
percentsFP=(0.0001)
percentsNA=(0.15)
k="0"

for id in {1..30}
do
	for fn in ${percentsFN[@]}
	do
		for fp in ${percentsFP[@]}
		do
			for na in ${percentsNA[@]}
			do	
				fpW=$(echo "$(echo $fn/$fp|bc -l)/1"|bc)
				f=$directory"/noisy/simID_"${id}"-n_"${n}"-m_"${m}"-fn_"${fn}"-fp_"${fp}"-na_"${na}"-k_"${k}".noisyMatrix"
				g=$directory"/ground/simID_"${id}"-n_"${n}"-m_"${m}"-k_"${k}".groundTruthMatrix"
				echo "Noisy: "$f
				echo "Ground: "$g
				python main.py -f $f -n 1 -p $fpW -o $o -g $g -z3path $z3
			done
			
		done
	done
done
