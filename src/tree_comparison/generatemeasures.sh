#!/bin/bash

foldergt=groundtruth
folderilp=ilp
folderz3=z3
folderwbo=wbo
filesgt="$(find ./${foldergt} -type f -name '*.txt' | grep 'simID_1-n' | sort)"
filesilp="$(find ./${folderilp} -type f -name '*.txt' | grep '*.output' | sort)"
filesz3="$(find ./${folderz3} -type f -name '*.txt' | grep '*.output' | sort)"
fileswbo="$(find ./${folderwbo} -type f -name '*.txt' | grep '*.output' | sort)"
index=1
for fgt in ${filesgt}
do
	echo "Filename: "$fgt
	#python Tree.py $fgt
	for i in {1..10}
	do
		filp=${filesilp[index]}
		fz3=${filesz3[index]}
		fwbo=${fileswbo[index]}
		echo $fgt $filp $fz3 $fwbo
		index=$((index+1))
	done
done
