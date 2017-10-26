#!/bin/bash


directory='../../data/simulated/25oct/ground'
percentsFN=(0.15 0.25)
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


:"
directory='../../data/simulated/25oct'
n='100'
m='40'
percentsFN=(0.15 0.25)
percentsFP=(0.0001)
percentsNA=(0.15)
percentsK=(0 1 2)
percentsS=(4 7)
cov='2000'
minVAF='0.05'
for id in {1..10}
do
	for s in ${percentsS[@]}
	do
		for k in ${percentsK[@]}
		do
			for fn in ${percentsFN[@]}
			do
				for fp in ${percentsFP[@]}
				do
					for na in ${percentsNA[@]}
					do
						g=${directory}/ground/simNo_${id}-n_${n}-m_${m}-s_${s}-minVAF_${minVAF}-cov_${cov}-k_${k}.SCnoNoise
						f=${directory}/noisy/simNo_${id}-n_${n}-m_${m}-s_${s}-minVAF_${minVAF}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}.SCnoisy
						echo $f
						python2 check.py $g $f $fn
					done
				done
			done
			
		done
	done
done
"
