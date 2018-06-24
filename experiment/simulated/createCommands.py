import pandas as pd
import subprocess
import time
import sys

file = open('run_data_1-2.sh', 'w')
file.write('#!/usr/bin/env bash\n')
file.write('''
killbg() {
    for p in "${pids[@]}" ; do
        kill "$p";
    done
}
trap "exit" INT TERM ERR
trap "kill 0" EXIT
trap killbg EXIT

pids=()\n''')

app = 'ilp'
ss = [10, 7, 4]
ks = [1, 2]
whichdata = 'data_1/'

cmdEXE = {}
cmdEXE['z3'] = 'python src/z3.py'
cmdEXE['ilp'] = 'python src/ilp.py'
cmdEXE['maxhs'] = './src/csp_maxsat -s /home/frashidi/_PhISCS/src/solver/maxhs'
cmdEXE['maxino'] = './src_/csp_maxsat -s /home/frashidi/_PhISCS/src/solver/maxino/maxino-2015-k16-static -i'
fns = ['0.15', '0.25']
timeout = 24*3600

df = pd.read_csv('_param_1.txt', index_col=0, sep='\t')

def run_helper(ss, ks, fns):
    pids =[]
    for i in range(1, 11):
        for s in ss:
            if s in [4, 7]:
                cov = 2000
            elif s in [10]:
                cov = 10000
            for k in ks:
                for fn in fns:
                    for fp in [0.0001]:
                        name = 'simNo_'+str(i)+'-n_100-m_40-s_'+str(s)+'-minVAF_0.05-cov_'+str(cov)+'-k_'+\
                        str(k)+'-fn_'+fn+'-fp_'+str(fp)+'-na_0.15.SCnoisy'
                        bulk = 'simNo_'+str(i)+'-n_100-m_40-s_'+str(s)+'-minVAF_0.05-cov_'+str(cov)+'-k_'+str(k)+'.bulk'
                        infile = whichdata + name
                        bulkfile = whichdata + bulk
                        odir = 'result/' + app
                        fn_rate = df.loc[name.replace('.SCnoisy',''), 'FN']
                        fp_rate = df.loc[name.replace('.SCnoisy',''), 'FP']                        
                        command = '{} -f {} -n {} -p {} -o {} -w {} -m {} -b {} -e {} -T {} --truevaf &'.format(cmdEXE[app], 
                                                                    infile, 
                                                                    fn_rate, 
                                                                    fp_rate, 
                                                                    odir, 
                                                                    0, 
                                                                    k, 
                                                                    bulkfile, 
                                                                    0,  
                                                                    timeout)
                        file.write(command+'\n')
                        file.write('pids+=($!)\n')
run_helper(ss, ks, fns)

file.write('\nwait')
file.close()