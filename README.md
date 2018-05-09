## SCePhy: A Constraint Satisfaction Approach for Tumor Phylogeny Reconstruction via Integrative use of Single Cell and Bulk Sequencing Data

#### Installation
```
git clone https://github.com/haghshenas/PhISCS.git
cd PhISCS
./configure
```


#### Description of the simulated data

For each ground matrix (.SCnoNoise) we added the following parameters to get the noisy matrix:

```
fn: false negative rate = {0.05, 0.10, 0.15, 0.25}
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