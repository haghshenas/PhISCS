#!/bin/bash

files="$(find ../../data/simulated/21oct/ground -type f -name '*.SCnoNoise' | sort)"

for f in ${files}
do
	echo "Filename: "$f
	Rscript unique.R $f
done