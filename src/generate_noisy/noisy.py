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
	file = file.replace('.txt','')
	f = file+'-fn_'+percfn+'-fp_'+percfp+'-na_'+percna+'-k_'+perck+'.noisyMatrix'
	df = pd.DataFrame(outresult)
	df = df.add_prefix('mut')
	df.index = ['cell'+str(row) for row in df.index]
	df.index.name = 'cellID/mutID'
	df.to_csv(f, sep='\t')

def introduce_false_both(data, n, m, percfn, percfp):
	countOne = 0;
	countZero = 0;
	indexFN = []
	indexFP = []
	for i in range(n):
		for j in range(m):
			if data[i][j] == 1:
				countOne = countOne + 1
				indexFN.append([i,j])
			elif data[i][j] == 0:
				countZero = countZero + 1
				indexFP.append([i,j])
	falsenegative = math.ceil(countOne * percfn)
	falsepositive = math.ceil(countZero * percfp)
	random.shuffle(indexFN)
	random.shuffle(indexFP)
	falsenegative = int(falsenegative)
	falsepositive = int(falsepositive)
	for i in range(falsenegative):
		[a,b] = indexFN[i]
		data[a][b] = 0
	for i in range(falsepositive):
		[a,b] = indexFP[i]
		data[a][b] = 1
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
	data = introduce_false_both(data, data.shape[0], data.shape[1], float(percfn), float(percfp))
	write_noisy_both(data, file, percfn, percfp, percna, perck)
