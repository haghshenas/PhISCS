# Description of the simulated data

For each ground matrix (.SCnoNoise) we added the following parameters to get the noisy matrix:

```
fn: false negative rate = {0.15, 0.25}
fp: false positive rate = {0.0001}
na: missing value rate = {0.15}
```

And the description for the file names is the following:

```
simNo: simulation number
n: number of cells
m: number of mutations
s: number of sub-clones
minVAF: minimume VAF
cov: coverage
k: ISA violation mutations
```