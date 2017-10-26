import numpy as np
import pandas as pd
import random
import sys
import math

def read_data(file):
	df = pd.read_table(file)
	df.drop('cellID/mutID', axis=1, inplace=True)
	return df.values

if __name__ == "__main__":
	
	groundF = sys.argv[1]
	noisyF = sys.argv[2]
	fn = sys.argv[3]
	
	ground = read_data(groundF)
	noisy = read_data(noisyF)

	countFP = 0
	countFN = 0
	countNA = 0
	noumberOfOne = 0
	numberOfOther = 0
	fn = float(fn)

	for i in range(ground.shape[0]):
		for j in range(ground.shape[1]):
			if ground[i][j] == 1:
				noumberOfOne = noumberOfOne+1
				if noisy[i][j] == 0:
					countFN = countFN+1
				elif noisy[i][j] == 1:
					1+1
				elif noisy[i][j] == 2:
					countNA = countNA+1
					numberOfOther = numberOfOther+1
				else:
					print 'Wrong Input'
					sys.exit(2)
			elif ground[i][j] == 0:
				if noisy[i][j] == 0:
					1+1
				elif noisy[i][j] == 1:
					countFP = countFP+1
				elif noisy[i][j] == 2:
					countNA = countNA+1
				else:
					print 'Wrong Input'
					sys.exit(2)

	print countNA,'\t', countFN,'\t',countFP,'\t',float(noumberOfOne*fn),'\t',float((noumberOfOne-numberOfOther)*fn),'\t',float(noumberOfOne*fn*0.85)
