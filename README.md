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

## Output
