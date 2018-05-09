#!/usr/bin/env python
from gurobipy import *
import numpy as np
from datetime import datetime
import argparse
import os
import errno

# ======== INFO
'''
This version of the ILP allows EVERITHING.
'''

# ======== COMMAND LINE THINGS
parser = argparse.ArgumentParser(description='big_brother', add_help=True)
# Required:
parser.add_argument('-f', '--file', required=True,
                    type=str,
                    help='Input matrix file')
parser.add_argument('-n', '--fnWeight', required=True,
                    type=int,
                    help='Weight for false negative')
parser.add_argument('-p', '--fpWeight', required=True,
                    type=int,
                    help='Weight for false negative')
parser.add_argument('-o', '--outDir', required=True,
                    type=str,
                    help='Output directory')
parser.add_argument('-m', '--colWeight', required=True,
                    type=int,
                    help='Weight of eliminated columns')

# Optional:
# parser.add_argument('-m', '--maxMut', default=0,
#                     type=int,
#                     help='Max number mutations to be eliminated [0]')

parser.add_argument('-t', '--threads', default=1,
                    type=int,
                    help='Number of threads [Default is 1]')
parser.add_argument('-b', '--bulk', default=None,
                    type=str,
                    help='Bulk sequencing file [""]')
parser.add_argument('-e', '--delta', default=0.01,
                    type=float,
                    help='Delta in VAF [0.01]')
parser.add_argument('--truevaf',  action='store_true',
                    help='Use tree VAFs')

args = parser.parse_args()

# ======== INPUT PROCESSING FOR DATA:
start_model = datetime.now()
DELIMITER = '\t'

verbose = False
tree = True

inp = np.genfromtxt(args.file, skip_header=1, delimiter=DELIMITER)

with open(args.file, 'r') as fin:
    mutation_names = fin.readline().strip().split(DELIMITER)[1:]
    cell_names = [x.strip().split(DELIMITER)[0] for x in fin]

matrix_input = np.delete(inp, 0, 1)

# =========== GENERAL INITIALIZATION
cells = matrix_input.shape[0]
mutations = matrix_input.shape[1]

# k_max = args.maxMut

fn_weight = args.fnWeight
fp_weight = args.fpWeight

using_bulk = False
if args.bulk:
    delta = args.delta
    using_bulk = True
    bulk_mutations = []
    with open(args.bulk, 'r') as bulkfile:
        bulkfile.readline()
        for line in bulkfile:
            values = line.split('\t')
            if args.truevaf:
                vaf = float(values[5].split(';')[1].split('=')[1])
            else:
                vaf = float(values[3]) / (float(values[4])+float(values[3]))
            bulk_mutations.append(vaf)

# =========== VARIABLES
model = Model('ILP')
model.Params.Threads = args.threads
model.Params.LogFile = ""

print('Generating variables...')

# --- Flips/Completion
F0 = {}
F1 = {}
X = {}
c = 0
while c < cells:
    m = 0
    while m < mutations:
        # 0->1 [False Negative / Allele dropout]
        if matrix_input[c][m] == 0:
            F0[c, m] = model.addVar(vtype=GRB.BINARY,
                                    obj=fn_weight,
                                    name='B({0},{1})'.format(c, m))
        else:
            F0[c, m] = 0

        # 1->0 [False Positive]
        if matrix_input[c][m] == 1:
            F1[c, m] = model.addVar(vtype=GRB.BINARY,
                                    obj=fp_weight,
                                    name='B({0},{1})'.format(c, m))
        else:
            F1[c, m] = 0
        # Missing values
        if matrix_input[c][m] == 2:
            X[c, m] = model.addVar(vtype=GRB.BINARY,
                                   obj=0,
                                   name='B({0},{1})'.format(c, m))
        else:
            X[c, m] = 0

        m += 1
    c += 1

# --- Conflict counter
B = {}
p = 0
while p < mutations:
    q = 0
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
                        obj=args.colWeight,
                        name='K[{0}]'.format(m))
    m += 1

if using_bulk:
    A = {}
    C1 = {}
    C2 = {}
    p = 0
    while p < mutations:
        q = 0
        while q < mutations:
            A[p, q] = model.addVar(vtype=GRB.BINARY, obj=0,
                                   name='A[{0},{1}]'.format(p, q))
            r = 0
            while r < cells:
                C1[r,p,q] = model.addVar(vtype=GRB.BINARY, obj=0)
                C2[r,p,q] = model.addVar(vtype=GRB.BINARY, obj=0)
                r += 1

            q += 1
        p += 1

model.modelSense = GRB.MINIMIZE
model.update()

# ====== CONSTRAINTS
print('Generating constraints...')

# --- sum K_i <= k_max
# model.addConstr(quicksum(K[m] for m in range(mutations)) <= k_max)

# --- B(p, q, a, b) variables
c = 0
while c < cells:
    p = 0
    while p < mutations:
        q = 0
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
    q = 0
    while q < mutations:
        model.addConstr(
            B[p, q, 0, 1] + B[p, q, 1, 0] + B[p, q, 1, 1]
            - K[p] - K[q]
            <= 2,
            'Conf[{0},{1}]'.format(p, q))
        q += 1
    p += 1

# --- Constraint for VAFs
if using_bulk:
    p = 0
    while p < mutations:
        q = 0
        while q < mutations:
            c = 0
            while c < cells:
                model.addConstr(C1[c,p,q] <= A[p, q])
                model.addConstr(C1[c,p,q] <= matrix_input[c, p] % 2 + F0[c, p] - F1[c, p] + X[c, p])
                model.addConstr(C1[c,p,q] >= matrix_input[c, p] % 2 + F0[c, p] - F1[c, p] + X[c, p] + A[p, q] - 1)

                model.addConstr(C2[c,p,q] <= A[p, q])
                model.addConstr(C2[c,p,q] <= matrix_input[c, q] % 2 + F0[c, q] - F1[c, q] + X[c, q])
                model.addConstr(C2[c,p,q] >= matrix_input[c, q] % 2 + F0[c, q] - F1[c, q] + X[c, q] + A[p, q] - 1)

                model.addConstr(C1[c,p,q] >= C2[c,p,q])
                c += 1

            model.addConstr(A[p, q] + A[q, p] <= 1)
            model.addConstr(A[p, q] <= 1 - K[p])
            model.addConstr(A[p, q] <= 1 - K[q])

            model.addConstr(A[q, p] <= 1 - K[p])
            model.addConstr(A[q, p] <= 1 - K[q])

            model.addConstr(A[p, q] * bulk_mutations[p] * (1 + delta)
                            >= A[p, q] * bulk_mutations[q])

            r = 0
            while r < mutations:
                model.addConstr(bulk_mutations[p] * (1 + delta) >= bulk_mutations[q] * (
                    A[p, q] - A[r, q] - A[q, r]) + bulk_mutations[r] * (A[p, r] - A[r, q] - A[q, r]))
                r += 1

            q += 1
        p += 1

time_to_model = datetime.now() - start_model
# ====== OPTIMIZE
start_optimize = datetime.now()

model.optimize()

# ====== POST OPTIMIZATION
if model.status == GRB.Status.INFEASIBLE:
    print('The model is unfeasible.')
    exit(0)



time_to_opt = datetime.now() - start_optimize
time_to_run = datetime.now() - start_model

if verbose:
    print('-' * 20)
    print('Time')
    # print(time_to_end)
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
    if verbose:
        print(' '.join([str(x) for x in row]))
    flip0_matrix.append(row)
    c += 1

flip0_matrix = np.array(flip0_matrix)

if verbose:
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
    if verbose:
        print(' '.join([str(x) for x in row]))
    flip1_matrix.append(row)
    c += 1

flip1_matrix = np.array(flip1_matrix)

try:
    os.makedirs(args.outDir)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(args.outDir):
        pass
    else:
        raise

filename = os.path.splitext(os.path.basename(args.file))[0]
outfile = os.path.join(args.outDir, filename)
file_out = open('{0}.ILP.conflictFreeMatrix'.format(outfile), 'w+')

# --- Solution info
removed_cols = []
removed_mutation_names = []
removed_mutation_indeces = []
solution_mutation_names = []
m = 0
while m < mutations:
    value = int(K[m].X)
    removed_cols.append(value)
    if value == 0:
        solution_mutation_names.append(mutation_names[m])
    else:
        removed_mutation_names.append(mutation_names[m])
        removed_mutation_indeces.append(str(m + 1))
    m += 1

# print(removed_cols)
print(removed_mutation_names)

file_out.write('cellID/mutID\t')
file_out.write('\t'.join(solution_mutation_names))
file_out.write('\n')

if verbose:
    print('-' * 20)
    print('Result')
sol_20_tot = 0
sol_21_tot = 0
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
                if int(X[c, m].X) == 0:
                    sol_20_tot += 1
                else:
                    sol_21_tot += 1
        m += 1
    if verbose:
        print(' '.join([str(x) for x in row]))
    file_out.write('%s\t' % cell_names[c])
    file_out.write('\t'.join([str(x) for x in row]))
    file_out.write('\n')

    sol_matrix.append(row)
    c += 1

sol_matrix = np.array(sol_matrix)

file_out.close()


log = open('{0}.ILP.log'.format(outfile), 'w+')
# --- Input info
log.write('FILE_NAME: {0}\n'.format(str(os.path.basename(args.file))))
log.write('NUM_CELLS(ROWS): {0}\n'.format(str(cells)))
log.write('NUM_MUTATIONS(COLUMNS): {0}\n'.format(str(mutations)))
log.write('FN_WEIGHT: {0}\n'.format(str(fn_weight)))
log.write('FP_WEIGHT: {0}\n'.format(str(fp_weight)))
log.write('NUM_THREADS: {0}\n'.format(str(args.threads)))
log.write('MODEL_SOLVING_TIME_SECONDS: {0:.3f}\n'.format(time_to_opt.total_seconds()))
log.write('RUNNING_TIME_SECONDS: {0:.3f}\n'.format(time_to_run.total_seconds()))


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

if conflict_free:
    conflict_free = 'YES'
else:
    conflict_free = 'NO'

log.write('IS_CONFLICT_FREE: {0}\n'.format(conflict_free))

log.write('TOTAL_FLIPS_REPORTED: {0}\n'.format(
    str(flip0_sol_tot + flip1_sol_tot)))
log.write('0_1_FLIPS_REPORTED: {0}\n'.format(
    str(flip0_sol_tot)))
log.write('1_0_FLIPS_REPORTED: {0}\n'.format(
    str(flip1_sol_tot)))
log.write('2_0_FLIPS_REPORTED: {0}\n'.format(
    str(sol_20_tot)))
log.write('2_1_FLIPS_REPORTED: {0}\n'.format(
    str(sol_21_tot)))
# log.write('MUTATIONS_REMOVED_UPPER_BOUND: {0}\n'.format(
#     str(args.maxMut)))
log.write('MUTATIONS_REMOVED_NUM: {0}\n'. format(
    str(sum(removed_cols))))
log.write('MUTATIONS_REMOVED_INDEX: {0}\n'.format(
    ','.join(removed_mutation_indeces)))

log.close()

if tree:
    # Tree construction
    from tree import *
    write_tree(sol_matrix, mutation_names, outfile)
