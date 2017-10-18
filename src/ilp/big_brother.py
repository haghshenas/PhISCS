#!/usr/bin/env python
from gurobipy import *
import numpy as np
from datetime import datetime
import argparse

# ======== INFO
'''
This version of the ILP allows EVERITHING.

Should be used for test purposes.
'''

# ======== COMMAND LINE THINGS
parser = argparse.ArgumentParser(description='big_brother', add_help=True)
parser.add_argument('-i', '--id', required = True,
					type = int,
					help = 'Simulation ID')
parser.add_argument('-fn', '--falseneg', required = True,
					type = float,
					help = 'False negative rate')
parser.add_argument('-fp', '--falsepos', required = True,
					type = float,
					help = 'False positive rate')
parser.add_argument('-c', '--cells', required = True,
					type = int,
					help = 'Number of cells')
parser.add_argument('-k', '--kmax', default = 0,
					type = int,
					help = 'Max number column removals [Default is 0]')
parser.add_argument('-d', '--dir', required = True,
					type = str,
					help = 'Simulation data directory (should contain ground/ and noisy/')
parser.add_argument('-t', '--threads', default = 4,
					type = int,
					help = 'Number of threads allowed [Default is 4]')
parser.add_argument('-u', '--custom', nargs=2, required = True,
				   type = int,
				   help = 'Custom weights for FN and FP')

args = parser.parse_args()

# ======== INPUT PROCESSING FOR NOISY DATA:

sim_id = args.id
fn_rate = args.falseneg
arg_cell = args.cells
fp_rate = args.falsepos

fp_str = ''
if fp_rate != float(0):
	fp_str = '-fp_{0}'.format(str(fp_rate))


folder = args.dir
sim_file = 'noisyFile-simID_{0}-n_{1}-m_50-fn_{2}{3}.txt'.format(
	str(sim_id), str(arg_cell), str(fn_rate), fp_str)

inp = np.genfromtxt(folder + '/noisy/' + sim_file, skip_header=1, delimiter='\t')

matrix_input = np.delete(inp, 0, 1)

with open(folder + '/noisy/' + sim_file, 'r') as fin:
	mutation_names = fin.readline().strip().split('\t')[1 :]
	cell_names = [ x.strip().split('\t')[0] for x in fin ]

print(mutation_names)
print(cell_names)

# =========== GENERAL INITIALIZATION

cells = matrix_input.shape[0]
mutations = matrix_input.shape[1]

# k_max = matrix_input.shape[1] * 0.1
k_max = args.kmax

fn_weight, fp_weight = args.custom

# =========== VARIABLES
model = Model('Reduced ILP')
model.Params.Threads = args.threads
# model.Params.timeLimit = 300.0

print('Generating variables...')

# --- Flips 0->1 [False Negative / Allele dropout]
F0 = {}
c = 0
while c < cells:
	m = 0
	while m < mutations:
		if matrix_input[c][m] == 0:
			F0[c, m] = model.addVar(vtype = GRB.BINARY,
							   obj = fn_weight,
							   name='B({0},{1})'.format(c, m))
		else:
			F0[c,m] = 0
		m += 1
	c += 1

# --- Flips 1->0 [False Positive]
F1 = {}
c = 0
while c < cells:
	m = 0
	while m < mutations:
		if matrix_input[c][m] == 1:
			F1[c, m] = model.addVar(vtype=GRB.BINARY,
							   obj= fp_weight,
							   name='B({0},{1})'.format(c, m))
		else:
			F1[c,m] = 0
		m += 1
	c += 1

# --- Missing values
X = {}
c = 0
while c < cells:
	m = 0
	while m < mutations:
		if matrix_input[c][m] == 2:
			X[c, m] = model.addVar(vtype=GRB.BINARY,
							   obj= 0,
							   name='B({0},{1})'.format(c, m))
		else:
			X[c,m] = 0
		m += 1
	c += 1


# --- Conflict counter
B = {}
p = 0
while p < mutations:
	q = p + 1
	while q < mutations:
		B[p, q, 1, 1] = model.addVar(vtype=GRB.BINARY, obj=0,
				name='B[{0},{1},1,1]'.format(p, q))
		B[p, q, 1, 0] = model.addVar(vtype=GRB.BINARY, obj=0,
				name='B[{0},{1},1,0]'.format(p, q))
		B[p, q, 0, 1] = model.addVar(vtype=GRB.BINARY, obj=0,
				name='B[{0},{1},0,1]'.format(p, q))
		q += 1
	p += 1


# --- Column delition
K = {}
m = 0
while m < mutations:
	K[m] = model.addVar(vtype=GRB.BINARY,
						obj=0,
						name='K[{0}]'.format(m))
	m += 1


model.modelSense = GRB.MINIMIZE
model.update()

# ====== CONSTRAINTS
print('Generating constraints...')

# --- sum K_i <= k_max
model.addConstr(quicksum(K[m] for m in range(mutations)) <= k_max)

# --- B(p, q, a, b) variables
c = 0
while c < cells:
	p = 0
	while p < mutations:
		q = p + 1
		while q < mutations:
			model.addConstr(
				(matrix_input[c, p] % 2 + F0[c, p] - F1[c, p] + X[c, p]) +
				(matrix_input[c, q] % 2 + F0[c, q] - F1[c, q] + X[c, q]) -
				B[p, q, 1, 1] <= 1,
				'B[{0},{1},1,1]_{2}'.format(p, q, c))
			model.addConstr(
				- (matrix_input[c, p] % 2 + F0[c, p] - F1[c, p] + X[c, p]) +
				(matrix_input[c, q] % 2 + F0[c, q] - F1[c, q] + X[c, q]) -
				B[p, q, 0, 1] <= 0,
				'B[{0},{1},0,1]_{2}'.format(p, q, c))
			model.addConstr(
				(matrix_input[c, p] % 2 + F0[c, p] - F1[c, p] + X[c, p]) -
				(matrix_input[c, q] % 2 + F0[c, q] - F1[c, q] + X[c, q]) -
				B[p, q, 1, 0] <= 0,
				'B[{0},{1},1,0]_{2}'.format(p, q, c))
			q += 1
		p += 1
	c += 1

# --- No conflict between columns
p = 0
while p < mutations:
	q = p + 1
	while q < mutations:
		model.addConstr(
			B[p, q, 0, 1] + B[p, q, 1, 0] + B[p, q, 1, 1]
			- K[p] - K[q]
			<= 2,
			'Conf[{0},{1}]'.format(p, q))
		q += 1
	p += 1

# ====== OPTIMIZE

start_optimize = datetime.now()
model.optimize()

# ====== POST OPTIMIZATION

print('-' * 20)
print('Time')
time_to_end = datetime.now() - start_optimize
print(time_to_end)


print('-' * 20)
print('Flipped 0 -> 1')
flip0_matrix = []
flip0_sol_tot = 0

c = 0
while c < cells:
	m = 0
	row = []
	while m < mutations:
		if not isinstance(F0[c, m], int):
			row.append(int(F0[c, m].X))
			flip0_sol_tot += int(F0[c, m].X)
		else:
			row.append(0)
		m += 1
	print(' '.join([str(x) for x in row]))
	flip0_matrix.append(row)
	c += 1

flip0_matrix = np.array(flip0_matrix)

print('-' * 20)
print('Flipped 1 -> 0')
flip1_matrix = []
flip1_sol_tot = 0
c = 0
while c < cells:
	m = 0
	row = []
	while m < mutations:
		if not isinstance(F1[c, m], int):
			row.append(int(F1[c, m].X))
			flip1_sol_tot += int(F1[c, m].X)
		else:
			row.append(0)
		m += 1
	print(' '.join([str(x) for x in row]))
	flip1_matrix.append(row)
	c += 1

flip1_matrix = np.array(flip1_matrix)


file_out = open('out/sol_{0}'.format(sim_file), 'w+')
log = open('out/log_{0}'.format(sim_file), 'w+')

print('-' * 20)
print('Result')
sol_matrix = []
c = 0
while c < cells:
	m = 0
	row = []
	while m < mutations:
		if int(K[m].X) == 0:
			if matrix_input[c, m] == 0:
				row.append(int(F0[c, m].X))
			elif matrix_input[c, m] == 1:
				row.append(1 - int(F1[c, m].X))
			else:
				row.append(int(X[c, m].X))
		m += 1
	print(' '.join([str(x) for x in row]))
	file_out.write(','.join([str(x) for x in row]))
	file_out.write('\n')

	sol_matrix.append(row)
	c += 1

sol_matrix = np.array(sol_matrix)

file_out.close()

# --- Input info
log.write('SIM_ID: {0}\n'.format(str(sim_id)))
log.write('NUM_MUTATIONS(COLUMNS): {0}\n'.format(str(mutations)))
log.write('NUM_ROWS(CELLS): {0}\n'.format(str(cells)))
log.write('RUNNING_TIME_SECONDS: {0}\n'.format(str(time_to_end.total_seconds())))
log.write('FALSE_NEGATIVE_RATE: {0}\n'.format(str(fn_rate)))

# -- Ground info
ground_file = 'simID_{0}-n_{1}-m_50.txt'.format(
	str(sim_id), str(arg_cell))
ground_matrix = np.genfromtxt(folder + '/ground/' + ground_file, skip_header=1, usecols=range(1, 51))

flips_in_noisy = 0
flips01_in_noisy = 0
flips10_in_noisy = 0
flips01_matrix = np.zeros((cells, mutations))
flips10_matrix = np.zeros((cells, mutations))
for c in range(cells):
	for m in range(mutations):
		if ground_matrix[c,m] == 0 and matrix_input[c,m] == 1:
			flips01_in_noisy += 1
			flips_in_noisy += 1
			flips01_matrix[c, m] = 1

		if ground_matrix[c,m] == 1 and matrix_input[c,m] == 0:
			flips10_in_noisy += 1
			flips_in_noisy += 1
			flips10_matrix[c, m] = 1

log.write('TOTAL_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: {0}\n'.format(
	str(flips_in_noisy)))
log.write('0_1_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: {0}\n'.format(
	str(flips01_in_noisy)))
log.write('1_0_FLIPS_INTRODUCED_BY_NOISY_COMPARED_TO_GROUND: {0}\n'.format(
	str(flips10_in_noisy)))

# --- Solution info
removed_cols = []
removed_mutation_names = []
solution_mutation_names = []
m = 0
while m < mutations:
	value = int(K[m].X)
	removed_cols.append(value)
	if value == 1:
		removed_mutation_names.append(str(m))
	m += 1

log.write('TOTAL_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: {0}\n'.format(
	str(flip0_sol_tot + flip1_sol_tot)))
log.write('0_1_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: {0}\n'.format(
	str(flip0_sol_tot)))
log.write('1_0_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: {0}\n'.format(
	str(flip1_sol_tot)))
log.write('COLUMNS REMOVED: {0}\n'. format(
	sum(removed_cols)))
log.write('MUTATIONS REMOVED: {}\n'.format(
	','.join(removed_mutation_names)))

# --- Overlap info

overlap010 = 0
overlap101 = 0
overlap_total = 0

for c in range(cells):
	for m in range(mutations):
		if flips01_matrix[c, m] == 1 and flip1_matrix[c, m] == 1:
			overlap010 += 1
			overlap_total += 1
		elif flips10_matrix[c, m] and flip0_matrix[c, m] == 1:
			overlap101 += 1
			overlap_total += 1
		elif flips01_matrix[c, m] == 1 and flip1_matrix[c, m] == 1:
			overlap_total += 1
		elif flips10_matrix[c, m] == 1 and flip0_matrix[c, m] == 1:
			overlap_total += 1

log.write('TOTAL_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: {0}\n'.format(
	str(overlap_total)))
log.write('0_1_0_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: {0}\n'.format(
	str(overlap010)))
log.write('1_0_1_OVERLAP_NOISE_FLIPS_SOLUTION_FLIPS: {0}\n'.format(
	str(overlap101)))

# --- DOUBLE-CHECK PP
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
			print('Conflict in columns (%d, %d)' % (p, q))

log.write('CONFLICT_FREE: {0}\n'.format(str(conflict_free)))
log.write('NUM_THREADS: {0}\n'.format(str(4)))
log.write('CPU_CLOCK: {0}\n'.format('2.7 GHz'))

log.close()

# Tree construction
from tree import *
write_tree_comp(sol_matrix, mutation_names, '%s' % sim_file)
