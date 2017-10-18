#!/bin/bash

#files="$(find ./input -type f -name '*.txt' | grep '6sep' | grep 'simID_1-n_10' | sort)"
files="$(find ./input -type f -name '*.txt' | grep '6sep' | sort)"

for f in ${files}
do
	echo $f
	python main.py $f
	rm ./output/temp*
done
