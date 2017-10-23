# Tumor Phylogeny Recontstruction using CSP and ILP
For every implementation (ILP, Z3, and Open-WBO) we should have **a single program that works on both simulated and real data sets**.
## Usage
```
usage: toolname [-h] -f FILE -n FNWEIGHT -p FPWEIGHT -o OUTDIR
                [-m MAXMUT] [-t THREADS]

Required arguments:
   -f, --file     STR        Input matrix file
   -n, --fnWeight INT        Weight for false negative
   -p, --fpWeight INT        Weight for false negative
   -o, --outDir   STR        Output directory

Optional arguments:
   -m, --maxMut   INT        Max number mutations to be eliminated [0]
   -t, --threads  INT        Number of threads [1]

Other arguments:
   -h, --help                Show this help message and exit
```

## Input
The input matrix file is assumed to be tab-delimited. This file has the following format for a matrix with _C_ cells and _M_ mutations:
```
cellID/mutID      mut1     mut2     mut3     ...      mutM
cell1             x        x        x        ...      x
cell2             x        x        x        ...      x
cell3             x        x        x        ...      x
...
cellC             x        x        x        ...      x
```
Where _x_ is in {0, 1, 2}. More specifically:
* The first line is the header line. First string is an arbitrary string and next _M_ strings are the names of mutations.
* Each of the next _C_ lines contains mutation information for a single cell. The first string is cell name and next _M_ integers show if a mutation is observed (1) or not (0). The value 2 means the information is not available (missing).

## Output
The program will generate two files in **OUT_DIR** folder (which is set by argument -o or --outDir).
#### 1. log file
Suppose the input file is **INPUT_MATRIX.ext**, the log will be stored in file **OUT_DIR/INPUT_MATRIX.log**. For example:
```
input file: simID_1-n_10-m_50-fn_0.05-fp_0.001-na_0-k_0.noisyMatrix
  log file: simID_1-n_10-m_50-fn_0.05-fp_0.001-na_0-k_0.log

input file: wang.txt
  log file: wang.log
```
The log file contains a summary for running the program on the input file. It should be in the following format:
<pre><code>FILE_NAME: STR
NUM_CELLS(ROWS): INT (INT >= 1)
NUM_MUTATIONS(COLUMNS): INT (INT >= 1)
FN_WEIGHT: INT (INT >= 1)
FP_WEIGHT: INT (INT >= 1)
NUM_THREADS: INT (INT >= 1)
MODEL_SOLVING_TIME_SECONDS: FLOAT (FLOAT > 0)
RUNNING_TIME_SECONDS: FLOAT (FLOAT > 0)
IS_CONFLICT_FREE: YES/NO
TOTAL_FLIPS_REPORTED: INT (INT >= 0)
0_1_FLIPS_REPORTED: INT (INT >= 0)
1_0_FLIPS_REPORTED: INT (INT >= 0)
2_0_FLIPS_REPORTED: INT (INT >= 0)
2_1_FLIPS_REPORTED: INT (INT >= 0)
MUTATIONS_REMOVED_UPPER_BOUND: INT (INT >= 0)
MUTATIONS_REMOVED_NUM: INT (0 <= INT <= MUTATIONS_REMOVED_UPPER_BOUND)
MUTATIONS_REMOVED_INDEX: [INT<sub>1</sub>,INT<sub>2</sub>,...,INT<sub>MUTATIONS_REMOVED_NUM</sub>] (1 <= INT<sub>i</sub> <= NUM_MUTATIONS for each 1 <= i <= MUTATIONS_REMOVED_NUM)
</code></pre>
#### 2. output matrix file
Suppose the input file is **INPUT_MATRIX.ext**, the output matrix will be stored in file **OUT_DIR/INPUT_MATRIX.output**. For example:
```
 input file: simID_1-n_10-m_50-fn_0.05-fp_0.001-na_0-k_0.noisyMatrix
output file: simID_1-n_10-m_50-fn_0.05-fp_0.001-na_0-k_0.output

 input file: wang.txt
output file: wang.output
```
The output file is also a tab-delimited file with the exact same format as the input file. The only difference compared to the input file is that _x_ values of the matrix are modified so that the matrix is conflict free.
