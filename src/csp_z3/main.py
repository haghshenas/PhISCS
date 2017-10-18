import numpy as np
import pandas as pd
from datetime import datetime
import argparse
import os
import sys


def read_data(file):
	df = pd.read_table(file)
	df.drop('cellID/mutID', axis=1, inplace=True)
	return df.values


def write_output(outresult, file):
	df = pd.DataFrame(outresult)
	df = df.add_prefix('mut')
	df.index = ['cell'+str(row) for row in df.index]
	df.index.name = 'cellID/mutID'
	df.to_csv(file, sep='\t')


def compare_flips(inp, output, n, m, zeroToOne):
	totalflip = 0
	for i in range(n):
		for j in range(m):
			if zeroToOne:
				if inp[i][j] == 0 and output[i][j] == 1:
					totalflip = totalflip + 1
			else:
				if inp[i][j] == 1 and output[i][j] == 0:
					totalflip = totalflip + 1
	return totalflip


def compare_na(inp, output, n, m, twoToZero):
	totalflip = 0
	for i in range(n):
		for j in range(m):
			if twoToZero:
				if inp[i][j] == 2 and output[i][j] == 0:
					totalflip = totalflip + 1
			else:
				if inp[i][j] == 2 and output[i][j] == 1:
					totalflip = totalflip + 1
	return totalflip


def compare_ground_solution(minput, mnoisy, moutput, n, m, zeroToOne):
	totalflip = 0
	for i in range(n):
		for j in range(m):
			if zeroToOne:
				if minput[i][j] == 0 and mnoisy[i][j] == 1 and moutput[i][j] == 0:
					totalflip = totalflip + 1
			else:
				if minput[i][j] == 1 and mnoisy[i][j] == 0 and moutput[i][j] == 1:
					totalflip = totalflip + 1
	return totalflip


def check_conflict_free(sol_matrix):
	conflict_free = True
	for p in range(sol_matrix.shape[1]):
		for q in range(p + 1, sol_matrix.shape[1]):
			oneone = False
			zeroone = False
			onezero = False
			for r in range(sol_matrix.shape[0]):
				if sol_matrix[r][p] == 1 and sol_matrix[r][q] == 1:
					oneone = True
				if sol_matrix[r][p] == 0 and sol_matrix[r][q] == 1:
					zeroone = True
				if sol_matrix[r][p] == 1 and sol_matrix[r][q] == 0:
					onezero = True
			if oneone and zeroone and onezero:
				conflict_free = False
	return conflict_free


def getX(i,j):
	return "X_" + str(i) + "_" + str(j)

def getY(i,j):
	return "Y_" + str(i) + "_" + str(j)

def getB(p,q,a,b):
	return "B_" + str(p) + "_" + str(q) + "_" + str(a) + "_" + str(b)


def produce_input(fstr, data, numCells, numMuts, allow_col_elim, fn_weight, fp_weight, maxCol):
	file = open(fstr, "w")
	#file.write("(check-sat-using smt :random-seed 1)\n")
	#file.write("(apply qflia)")
	#file.write("(check-sat-using simplify)\n")
	#file.write("(check-sat-using qflia)\n")
	file.write("(check-sat-using sat)\n")
	for i in range(numCells):
		for j in range(numMuts):
			file.write("(declare-const X_" + str(i) + "_" + str(j) + " Bool)\n")
			file.write("(declare-const Y_" + str(i) + "_" + str(j) + " Bool)\n")		

	for p in range(numMuts):
		for q in range(numMuts):
			file.write("(declare-const B_" + str(p) + "_" + str(q) + "_0_1 Bool)\n")
			file.write("(declare-const B_" + str(p) + "_" + str(q) + "_1_0 Bool)\n")
			file.write("(declare-const B_" + str(p) + "_" + str(q) + "_1_1 Bool)\n")

	if allow_col_elim:
		for j in range(numMuts):
			file.write("(declare-const K_"+str(j)+" Bool)\n")
	else:
		K = []

	# Objective
	for i in range(numCells):
		for j in range(numMuts):
			if data[i][j] == 0:
				file.write("(assert-soft (= "+getX(i,j)+" true) :weight -"+str(fn_weight)+ ")\n")
				file.write("(assert (= "+getX(i,j)+" "+getY(i,j)+"))")
			elif data[i][j] == 1:
				file.write("(assert-soft (= "+getX(i,j)+" true) :weight -"+str(fp_weight)+")\n")
				file.write("(assert (not (= "+getX(i,j)+" "+getY(i,j)+")))")
			elif data[i][j] == 2:# NA Values
				file.write("(assert (= "+getX(i,j)+" "+getY(i,j)+"))")
				#file.write("(assert-soft (= X_"+str(i)+"_"+str(j)+" true) :weight -"+str((data[:,j]==0).sum())+")\n")
				#file.write("(assert-soft (= X_"+str(i)+"_"+str(j)+" false) :weight -"+str((data[:,j]==1).sum())+")\n")
				#file.write("(assert (= "+getX(i,j)+" true))\n")
				#file.write("(assert-soft (= "+getY(i,j)+" true) :weight -"+str((data[:,j]==0).sum())+")\n")
				#file.write("(assert-soft (= "+getY(i,j)+" false) :weight -"+str((data[:,j]==1).sum())+")\n")
			else:
				print("Error. Data entry in matrix " + f + " not equal to any of 0,1,2. EXITING !!!")
				sys.exit(2)


	# Constraint for not allowing removed columns go further than maxCol
	if allow_col_elim:
		for combo in combinations(range(m), maxCol+1):
			temp = "(assert-soft (not (and"
			for i in combo:
				temp = temp + " K_"+str(i)
			temp = temp + ")) :weight 1000)\n"
			file.write(temp)

	# Constraint for checking conflict
	for i in range(numCells):
		for p in range(numMuts):
			for q in range(numMuts):
				if p <= q:
					file.write("(assert (or (not "+getY(i,p)+") (not "+getY(i,q)+") "+getB(p,q,1,1)+"))\n")	
					file.write("(assert (or "+getY(i,p)+" (not "+getY(i,q)+") "+getB(p,q,0,1)+"))\n")
					file.write("(assert (or (not "+getY(i,p)+")  "+getY(i,q)+" "+getB(p,q,1,0)+"))\n")
					file.write("(assert (or (not "+getB(p,q,0,1)+") (not "+getB(p,q,1,0)+") (not "+getB(p,q,1,1)+")))")
					#add column elimination later

	file.write("(check-sat)\n")
	file.write("(get-model)\n")


def exe_command(file):
	command = "../../../z3-master/build/z3 -smt2 " + file + " > " + file.replace('temp1', 'temp2')
	os.system(command)


def read_ouput(n, m, fstr, allow_col_elim):
	file = open(fstr, "r")
	lines = file.readlines()
	i = -1
	j = -1
	outresult = -1*np.ones(shape=(n, m)).astype(int)
	col_el = []

	if allow_col_elim:
		for index in range(len(lines)):
			line = lines[index]
			if "define-fun K" in line:
				next_line = lines[index+1]
				i = line.split(' ')[3].split('_')[1]
				i = int(i)
				if "true" in next_line:
					col_el.append(i+1)

	for index in range(len(lines)):
		line = lines[index]
		if "define-fun Y" in line:
			i = line.split(' ')[3].split('_')[1]
			j = line.split(' ')[3].split('_')[2]
			i = int(i)
			j = int(j)
			next_line = lines[index+1]
			if j+1 in col_el:
				outresult[i][j] = -1
			else:
				if "true" in next_line:
					outresult[i][j] = 1
				else:
					outresult[i][j] = 0

	return outresult, col_el


if __name__ == "__main__":

	inFile = sys.argv[1]
	fid = sys.argv[2]
	row = sys.argv[3]
	col = sys.argv[4]
	perfn = sys.argv[5]
	perfp = sys.argv[6]
	outDir = sys.argv[7]

	inFile='../../data/simulated/17oct/noisy/simID_'+fid+'-n_'+row+'-m_'+col+'-fn_'+perfn+'-fp_'+perfp+'-na_0-k_0.noisyMatrix'
	logFile = outDir+'/simID_'+fid+'-n_'+row+'-m_'+col+'-fn_'+perfn+'-fp_'+perfp+'.txt'
	groundFile = '../../data/simulated/17oct/ground/simID_'+fid+'-n_'+row+'-m_'+col+'.txt'
	log = open(logFile, 'w')
	
	row = int(row)
	col = int(col)
	perfn = float(perfn)
	perfp = float(perfp)
	
	# Parameters
	''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< '''
	real_data = False
	allow_col_elim = False
	maxCol = int(col/10)
	fn_weight = 1
	#fp_weight = 30
	fp_weight = int(float(perfn)/float(perfp))
	''' >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> '''
	

	log.write('SIM_ID: '+fid+'\n')
	log.write('NUM_MUTATIONS(COLUMNS): '+str(col)+'\n')
	log.write('NUM_ROWS(CELLS): '+str(row)+'\n')

	noisy_data = read_data(inFile)
	t0 = datetime.now()
	produce_input(logFile.replace('.txt','.temp1'), noisy_data, row, col, allow_col_elim, fn_weight, fp_weight, maxCol)
	total_model = datetime.now()-t0
	t0 = datetime.now()
	exe_command(logFile.replace('.txt','.temp1'))
	total_running = datetime.now()-t0
	output_data, col_el = read_ouput(row, col, logFile.replace('.txt','.temp2'), allow_col_elim)
	
	log.write('MODEL_BUILD_TIME_SECONDS: '+str(total_model.total_seconds())+'\n')
	log.write('RUNNING_TIME_SECONDS: '+str(total_running.total_seconds())+'\n') 
	log.write('FALSE_NEGATIVE_RATE: '+str(perfn)+'\n')
	log.write('FALSE_POSITIVE_RATE: '+str(perfp)+'\n')

	if not real_data:
		ground_data = read_data(groundFile)
		a = compare_flips(ground_data, noisy_data, row, col, True)
		b = compare_flips(ground_data, noisy_data, row, col, False)
		log.write('TOTAL_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: '+str(a+b)+'\n')
		log.write('0_1_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: '+str(a)+'\n')
		log.write('1_0_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: '+str(b)+'\n')	
		a = compare_flips(noisy_data, output_data, row, col, True)
		b = compare_flips(noisy_data, output_data, row, col, False)
		log.write('TOTAL_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: '+str(a+b)+'\n')
		log.write('0_1_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: '+str(a)+'\n')
		log.write('1_0_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: '+str(b)+'\n')
	else:
		a = compare_flips(noisy_data, output_data, row, col, True)
		b = compare_flips(noisy_data, output_data, row, col, False)
		c = compare_na(noisy_data, output_data, row, col, True)
		d = compare_na(noisy_data, output_data, row, col, False)
		log.write('Total: '+str(a+b+c+d)+'\n')
		log.write('0->1_Flips: '+str(a)+'\n')
		log.write('1->0_Flips: '+str(b)+'\n')
		log.write('2->0_Flips: '+str(c)+'\n')
		log.write('2->1_Flips: '+str(d)+'\n')
	if allow_col_elim:
		log.write('UPPER_BOUND_COLUMNS_REMOVED:'+str(maxCol)+'\n')
		log.write('COLUMNS_REMOVED: '+str(len(col_el))+'\n')
		temp = 'MUTATIONS_REMOVED: '+ "," . join([str(i) for i in col_el])
		log.write(temp+'\n')
	if not real_data:
		ground_data = read_data(groundFile)
		a = compare_ground_solution(ground_data, noisy_data, output_data, row, col, True)
		b = compare_ground_solution(ground_data, noisy_data, output_data, row, col, False)
		log.write('TOTAL_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: '+str(a+b)+'\n')
		log.write('0_1_0_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: '+str(a)+'\n')
		log.write('1_0_1_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: '+str(b)+'\n')
	log.write('CONFLICT_FREE: '+str(check_conflict_free(output_data))+'\n')
	log.write('NUM_THREADS: 1'+'\n')
	log.write('CPU_CLOCK: 3.13 GHz'+'\n')
	
	write_output(output_data, logFile.replace('.txt','.out'))
	
