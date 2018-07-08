import pandas as pd
import subprocess
import time
import sys

file = open('_simulated1.sh', 'w')
# file.write('#!/usr/bin/env bash\n')
# file.write('''
# killbg() {
#	 for p in "${pids[@]}" ; do
#		 kill "$p";
#	 done
# }
# trap "exit" INT TERM ERR
# trap "kill 0" EXIT
# trap killbg EXIT

# pids=()\n''')

app = 'ilp'
ss = [10, 7, 4]
ks = [2, 1]
whichdata = 'data/'

cmdEXE = {}
cmdEXE['z3'] = 'python src/z3.py'
cmdEXE['ilp'] = 'python src/ilp.py'
cmdEXE['maxhs'] = './src/csp_maxsat -s /home/frashidi/_PhISCS/src/solver/maxhs'
cmdEXE['maxino'] = './src_/csp_maxsat -s /home/frashidi/_PhISCS/src/solver/maxino/maxino-2015-k16-static -i'
fns = ['0.05', '0.10', '0.15', '0.25']
timeout = 24*3600

df = pd.read_csv('_param.txt', index_col=0, sep='\t')

def run_helper(ss, ks, fns):
	pids =[]
	for k in ks:
		for s in ss:
			cov = 10000
			for fn in fns:
				for fp in [0.0001]:
					for i in range(1, 11):
						name = 'simNo_'+str(i)+'-n_100-m_40-s_'+str(s)+'-minVAF_0.05-cov_'+str(cov)+'-k_'+\
						str(k)+'-fn_'+fn+'-fp_'+str(fp)+'-na_0.15.SCnoisy'
						bulk = 'simNo_'+str(i)+'-n_100-m_40-s_'+str(s)+'-minVAF_0.05-cov_'+str(cov)+'-k_'+str(k)+'.bulk'
						infile = whichdata + name
						bulkfile = whichdata + bulk
						odir = 'result/' + app
						fn_rate = df.loc[name.replace('.SCnoisy',''), 'FN']
						fp_rate = df.loc[name.replace('.SCnoisy',''), 'FP']
						command = '{} -f {} -fn {:.3f} -fp {:.6f} -o {} -w {} -kmax {} -b {} -e {} --timeout {} --truevaf'.format(cmdEXE[app], 
																	infile, 
																	fn_rate, 
																	fp_rate, 
																	odir, 
																	0, 
																	k, 
																	bulkfile, 
																	0.05, 
																	timeout)
						file.write(command+'\n')
						# file.write('pids+=($!)\n')
run_helper(ss, ks, fns)

# file.write('\nwait')
file.close()