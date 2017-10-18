# Tumor Phylogeny Recontstruction using CSP and ILP

## Usage
```
toolname -f INPUT_MATRIX -n FN_WEIGHT -p FP_WEIGHT -o OUT_DIR [-g GROUND_TRUTH_MATRIX]
         [-m MAX_MUT] [-c MAX_CELL] [-t THREADS] [-h]

Required arguments:
   -f, --file     STR        Input matrix file
   -n, --fnWeight INT        Weight for false negative
   -p, --fpWeight INT        Weight for false negative
   -o, --outDir   STR        Output directory

Optional arguments:
   -g, --ground   STR        Ground truth matrix [""]
   -m, --maxMut   INT        Max number mutations to be eliminated [0]
   -c, --maxCell  INT        Max number cells to be eliminated [0]
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
Where x is in {0, 1, 2}. More specifically:
* The first line is the header line. First string is an arbitrary string and next _M_ strings are the names of mutations.
* Each of the next _C_ lines contains mutation information for a single cell. The first string is cell name and next _M_ integers show if a mutation is observed (1) or not (0). The value 2 means the information is not available (missing).

## Output
