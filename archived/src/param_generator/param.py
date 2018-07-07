import numpy as np
import pandas as pd

df = pd.DataFrame({'FN' : [], 'FP' : []})

def norm():
	x = 0
	while x == 0:
		y = np.random.normal(1, 0.1)
		if y > 0.5 and y < 2:
			x = y
	return x

for i in range(1,11):
	for s in [4, 7, 10]:
		cov = 10000
		for k in [0, 1, 2]:
			for fn in [0.05, 0.10, 0.15, 0.25]:
				for fp in [0.0001]:
					fn_temp = '%.2f' % fn
					name = 'simNo_'+str(i)+'-n_100-m_40-s_'+str(s)+'-minVAF_0.05-cov_'+\
							str(cov)+'-k_'+str(k)+'-fn_'+fn_temp+'-fp_'+str(fp)+'-na_0.15'
					a = '%.3f' % round(fn*norm(),3)
					b = '%.6f' % round(fp*norm(),6)
					df2 = pd.DataFrame([[a, b]], index=[name], columns=['FN', 'FP'])
					df = df.append(df2)


print(df)

df.to_csv('param.txt', sep='\t')


'''
df = pd.read_csv('~/Desktop/param.txt', index_col=0, sep='\t')
print df.loc['simNo_5-n_100-m_40-s_7-minVAF_0.05-cov_2000-k_2-fn_0.25-fp_0.0001-na_0.15', 'FN']
'''