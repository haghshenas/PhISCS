import numpy as np
import pandas as pd
import random
import sys
import math

def read_data(file):
	df = pd.read_table(file)
	df.drop('cellID/mutID', axis=1, inplace=True)
	return df.values

def write_noisy_both(outresult, file, percfn, percfp, percna, perck):
	file = file.replace('ground','noisy')
	file = file.replace('-k_0.noisyTruthMatrix','')
	f = file+'-fn_'+percfn+'-fp_'+percfp+'-na_'+percna+'-k_'+perck+'.noisyMatrix'
	df = pd.DataFrame(outresult)
	df = df.add_prefix('mut')
	df.index = ['cell'+str(row) for row in df.index]
	df.index.name = 'cellID/mutID'
	df.to_csv(f, sep='\t')

def introduce_false_both(data, n, m, percfn, percfp, percna):
	countOne = 0
	countZero = 0
	countOneZero = 0
	indexFN = []
	indexFP = []
	indexNA = []
	changedBefore = []
	for i in range(n):
		for j in range(m):
			countOneZero = countOneZero + 1
			indexNA.append([i,j])
			if data[i][j] == 1:
				countOne = countOne + 1
				indexFN.append([i,j])
			elif data[i][j] == 0:
				countZero = countZero + 1
				indexFP.append([i,j])
	falsenegative = math.ceil(countOne * percfn)
	falsepositive = math.ceil(countZero * percfp)
	nas = math.ceil(countOneZero * percna)
	random.shuffle(indexFN)
	random.shuffle(indexFP)
	random.shuffle(indexNA)
	for i in range(int(nas)):
		[a,b] = indexNA[i]
		#print "NA: ", [a,b]
		changedBefore.append([a,b])
		data[a][b] = 2
	counter = int(falsenegative)-1
	p = 0
	while counter>=0:
		if indexFN[p] in changedBefore:
			p = p+1
		else:
			p = p+1
			[a,b] = indexFN[p]
			#print "FN: ", [a,b]
			data[a][b] = 0
			counter = counter - 1
	counter = int(falsepositive)-1
	p = 0
	while counter>=0:
		if indexFP[p] in changedBefore:
			p = p+1
		else:
			p = p+1
			[a,b] = indexFP[p]
			#print "FP: ",[a,b]
			data[a][b] = 1
			counter = counter - 1
	return data


if __name__ == "__main__":

	random.seed(1)
	
	file = sys.argv[1]
	percfn = sys.argv[2]
	percfp = sys.argv[3]
	percna = sys.argv[4]
	perck = sys.argv[5]
	
	data = read_data(file)
	
	#data = introduce_false_both(data, n, m, float(percfn), float(percfp), float(percna), float(perck))
	data = introduce_false_both(data, data.shape[0], data.shape[1], float(percfn), float(percfp), float(percna))
	write_noisy_both(data, file, percfn, percfp, percna, perck)
