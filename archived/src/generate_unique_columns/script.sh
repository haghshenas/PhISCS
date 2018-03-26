#!/bin/bash

files="$(find ~/Desktop/result -type f -name '*.output' | sort)"

for f in ${files}
do
	echo "Filename: "$f
	Rscript unique.R $f
done