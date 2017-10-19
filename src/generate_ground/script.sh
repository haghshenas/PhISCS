#!/bin/bash

directory="../../data/simulated/17oct/ground"

files="$(find $directory -type f -name '*.groundTruthMatrix' | sort --version-sort)"

sid="1"

for f in ${files}
do
	echo "Filename: "$f
	python2 ground.py $f $sid
	sid=$((sid+1))
done