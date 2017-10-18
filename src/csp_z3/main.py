import numpy as np
import pandas as pd
from datetime import datetime
import argparse
import os
import sys


def read_data(fstr, fid, col, row, perfn, perfp, isGround):
	if isGround:
		f = fstr + 'simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'.txt'
	else:
		if perfp > 0:
			f = fstr + 'simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'-fp_'+str(perfp)+'.txt'
		else:
			f = fstr + 'simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'.txt'
			
	df = pd.read_table(f)
	df.drop('cellID/mutID', axis=1, inplace=True)
	return df.values # returns an ordinary matrix of dimensions row x col


def write_output(outresult, fstr, fid, col, row, perfn, perfp):
	if perfp > 0:
		f = fstr + 'outputFile-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'-fp_'+str(perfp)+'.txt'
	elif perfn > 0:
		f = fstr + 'outputFile-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'.txt'
	else:
		f = fstr + 'outputFile-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'.txt'
	df = pd.DataFrame(outresult)
	df = df.add_prefix('mut')
	df.index = ['cell'+str(row) for row in df.index]
	df.index.name = 'cellID/mutID'
	df.to_csv(f, sep='\t')


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


def produce_input(data, n, m, allow_col_elim, fn_weight, fp_weight, fstr, fid, col, row, perfn, perfp, maxCol):
	if perfp > 0:
		f = fstr + 'temp1-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'-fp_'+str(perfp)+'.txt'
	elif perfn > 0:
		f = fstr + 'temp1-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'.txt'
	else:
		f = fstr + 'temp1-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'.txt'
	
	file = open(f, "w")	
	numCells = n
	numMuts  = m
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
		for j in range(m):
			file.write("(declare-const K_"+str(j)+" Bool)\n")
	else:
		K = []

	# Objective
	for i in range(n):
		for j in range(m):
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
		c = maxCol
		for combo in combinations(range(m), c+1):
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


def exe_command(fstr, fid, col, row, perfn, perfp):
	if perfp > 0:
		f = fstr + 'temp1-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'-fp_'+str(perfp)+'.txt'
	elif perfn > 0:
		f = fstr + 'temp1-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'.txt'
	else:
		f = fstr + 'temp1-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'.txt'
	
	command = "../z3-master/build/z3 -smt2 " + f + " > " + f.replace('temp1', 'temp2')
	os.system(command)


def read_ouput(n, m, fstr, fid, col, row, perfn, perfp, allow_col_elim, data):
	if perfp > 0:
		f = fstr + 'temp2-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'-fp_'+str(perfp)+'.txt'
	elif perfn > 0:
		f = fstr + 'temp2-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'-fn_'+str(perfn)+'.txt'
	else:
		f = fstr + 'temp2-simID_'+str(fid)+'-n_'+str(row)+'-m_'+str(col)+'.txt'

	file = open(f, "r")
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
	
	#f = './input/6sep/noisyFile-simID_1-n_50-m_50-fn_0.3.txt'
	f = './input/13oct/noisyFile-simID_12-n_47-m_40-fn_0.22.txt'
	#f = './input/13oct/noisyFile-simID_11-n_115-m_16-fn_0.22.txt'
	#f = './input/2oct/noisyFile-simID_1-n_10-m_50-fn_0.3-fp_0.01.txt'
	#f = sys.argv[1]

	f_names = f.split("noisyFile")
	f_names[1] = f_names[1].replace('.txt', '')
	fid = f_names[1].split('_')[1].split('-')[0]
	col = f_names[1].split('_')[3].split('-')[0]
	row = f_names[1].split('_')[2].split('-')[0]
	perfn = f_names[1].split('_')[4].split('-')[0]
	try:
		perfp = f_names[1].split('_')[5]
		f = './output/' + 'logFile-simID_'+fid+'-n_'+row+'-m_'+col+'-fn_'+perfn+'-fp_'+perfp+'.txt'
	except IndexError:
		perfp = -1
		f = './output/' + 'logFile-simID_'+fid+'-n_'+row+'-m_'+col+'-fn_'+perfn+'.txt'

	logfile = open(f, 'w')
	logfile.write('SIM_ID: '+str(fid)+'\n')
	logfile.write('NUM_MUTATIONS(COLUMNS): '+str(col)+'\n')
	logfile.write('NUM_ROWS(CELLS): '+str(row)+'\n')
	row = int(row)
	col = int(col)
	noisy_data = read_data(f_names[0]+'noisyFile-', fid, col, row, perfn, perfp, False)
	

	# Parameters
	''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< '''
	real_data = True
	allow_col_elim = False
	maxCol = int(col/10)
	fn_weight = 1
	fp_weight = 30
	#fp_weight = int(float(perfn)/float(perfp))
	''' >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> '''
	

	t0 = datetime.now()
	produce_input(noisy_data, row, col, allow_col_elim, fn_weight, fp_weight, 
					'./output/', fid, col, row, perfn, perfp, maxCol)
	total_model = datetime.now()-t0
	t0 = datetime.now()
	exe_command('./output/', fid, col, row, perfn, perfp)
	total_running = datetime.now()-t0
	output_data, col_el = read_ouput(row, col, './output/', fid, col, row, perfn, perfp, allow_col_elim, noisy_data)
	
	logfile.write('MODEL_BUILD_TIME_SECONDS: '+str(total_model.total_seconds())+'\n')
	logfile.write('RUNNING_TIME_SECONDS: '+str(total_running.total_seconds())+'\n') 
	logfile.write('FALSE_NEGATIVE_RATE: '+str(perfn)+'\n')
	if perfp > 0:
		logfile.write('FALSE_POSITIVE_RATE: '+str(perfp)+'\n')
	if not real_data:
		ground_data = read_data('./input/ground/', fid, col, row, perfn, perfp, True)
		a = compare_flips(ground_data, noisy_data, row, col, True)
		b = compare_flips(ground_data, noisy_data, row, col, False)
		logfile.write('TOTAL_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: '+str(a+b)+'\n')
		logfile.write('0_1_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: '+str(a)+'\n')
		logfile.write('1_0_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: '+str(b)+'\n')	
		a = compare_flips(noisy_data, output_data, row, col, True)
		b = compare_flips(noisy_data, output_data, row, col, False)
		logfile.write('TOTAL_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: '+str(a+b)+'\n')
		logfile.write('0_1_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: '+str(a)+'\n')
		logfile.write('1_0_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: '+str(b)+'\n')
	else:
		a = compare_flips(noisy_data, output_data, row, col, True)
		b = compare_flips(noisy_data, output_data, row, col, False)
		c = compare_na(noisy_data, output_data, row, col, True)
		d = compare_na(noisy_data, output_data, row, col, False)
		logfile.write('Total: '+str(a+b+c+d)+'\n')
		logfile.write('0->1_Flips: '+str(a)+'\n')
		logfile.write('1->0_Flips: '+str(b)+'\n')
		logfile.write('2->0_Flips: '+str(c)+'\n')
		logfile.write('2->1_Flips: '+str(d)+'\n')
	if allow_col_elim:
		logfile.write('UPPER_BOUND_COLUMNS_REMOVED:'+str(maxCol)+'\n')
		logfile.write('COLUMNS_REMOVED: '+str(len(col_el))+'\n')
		temp = 'MUTATIONS_REMOVED: '+ "," . join([str(i) for i in col_el])
		logfile.write(temp+'\n')
	if not real_data:
		ground_data = read_data('./input/ground/', fid, col, row, perfn, perfp, True)
		a = compare_ground_solution(ground_data, noisy_data, output_data, row, col, True)
		b = compare_ground_solution(ground_data, noisy_data, output_data, row, col, False)
		logfile.write('TOTAL_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: '+str(a+b)+'\n')
		logfile.write('0_1_0_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: '+str(a)+'\n')
		logfile.write('1_0_1_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: '+str(b)+'\n')
	logfile.write('CONFLICT_FREE: '+str(check_conflict_free(output_data))+'\n')
	logfile.write('NUM_THREADS: 1'+'\n')
	logfile.write('CPU_CLOCK: 3.13 GHz'+'\n')
	
	write_output(output_data, "./output/" , fid, col, row, perfn, perfp)
	
