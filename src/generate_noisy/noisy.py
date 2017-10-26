import numpy as np
import pandas as pd
import random
import sys
import math

def read_data(file):
	df = pd.read_table(file)
	df.drop('cellID/mutID', axis=1, inplace=True)
	return df.values

def shouldIFlip():
	if random.choice([i for i in range(10000)]) == 475:
		return True
	else:
		return False

def toss(p):
    return True if random.random() < p else False

def write_noisy_both(outresult, file, percfn, percfp, percna):
	file = file.replace('ground','noisy')
	file = file.replace('.SCnoNoise','')
	f = file+'-fn_'+percfn+'-fp_'+percfp+'-na_'+percna+'.SCnoisy'
	df = pd.DataFrame(outresult)
	df = df.add_prefix('mut')
	df.index = ['cell'+str(row) for row in df.index]
	df.index.name = 'cellID/mutID'
	df.to_csv(f, sep='\t')

def introduce_false_both(data, n, m, percfn, percfp, percna):
	data2 = -1*np.ones(shape=(n, m)).astype(int)
	countFP = 0
	countFN = 0
	countNA = 0
	countOneZero = 0
	indexNA = []
	changedBefore = []
	for i in range(n):
		for j in range(m):
			indexNA.append([i,j])
			countOneZero = countOneZero + 1
	random.shuffle(indexNA)
	nas = math.ceil(countOneZero * percna)
	for i in range(int(nas)):
		[a,b] = indexNA[i]
		#print "NA: ", [a,b]
		changedBefore.append([a,b])
		data2[a][b] = 2
		countNA = countNA+1
	for i in range(n):
		for j in range(m):
			if data2[i][j] != 2:
				if data[i][j] == 1:
					if toss(percfn):
						data2[i][j] = 0
						countFN = countFN+1
						#print 'FN:','(cell',i,',mut',j,')'
					else:
						data2[i][j] = data[i][j]
				elif data[i][j] == 0:
					if toss(percfp):
					#if shouldIFlip():
						data2[i][j] = 1
						countFP = countFP+1
						#print 'FP:','(cell',i,',mut',j,')'
					else:
						data2[i][j] = data[i][j]
				else:
					print 'Wrong Input'
					sys.exit(2)

	print countNA,'\t',countFN,'\t',countFP
	return data2


if __name__ == "__main__":

	file = sys.argv[1]
	percfn = sys.argv[2]
	percfp = sys.argv[3]
	percna = sys.argv[4]

	simNo = int(file.split('simNo_')[-1].split('-')[0])
	n = int(file.split('n_')[-1].split('-')[0])
	m = int(file.split('m_')[-1].split('-')[0])
	s = int(file.split('s_')[-1].split('-')[0])
	minVAF = float(file.split('minVAF_')[-1].split('-')[0])
	cov = int(file.split('cov_')[-1].split('-')[0])
	k = int(file.split('k_')[-1].replace('.SCnoNoise',''))
	#random.seed(simNo+n+m+s+minVAF+cov+k+float(percfn)+float(percfp)+float(percna))

	
	data = read_data(file)
	
	data1 = introduce_false_both(data, data.shape[0], data.shape[1], float(percfn), float(percfp), float(percna))
	write_noisy_both(data1, file, percfn, percfp, percna)
