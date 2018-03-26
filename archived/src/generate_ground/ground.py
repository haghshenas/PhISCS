import numpy as np
import pandas as pd
import sys


inputF = sys.argv[1]
sid = sys.argv[2]

df = pd.read_table(inputF)
nrow = df.shape[0]
times = int(100/nrow)
tobechange = inputF.split('-n_')[0].replace('simID_','')
tobechange = tobechange.replace('../../data/simulated/17oct/ground/','')
df = pd.concat([df]*int(times), ignore_index=True)
df['cellID/mutID'] = ['cell'+str(row) for row in df.index]
outputF = inputF.replace('17oct','19oct')
outputF = outputF.replace('n_'+str(nrow), 'n_100')
outputF = outputF.replace('simID_'+tobechange, 'simID_'+str(sid))
df.to_csv(outputF, sep='\t', index=False)
