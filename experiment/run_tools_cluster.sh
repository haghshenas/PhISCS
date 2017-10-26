#!/bin/bash

experiment="colElimWeight"
currDir=`pwd`
dataDir="${currDir}/../data/simulated/21oct"
outPre="${currDir}/results/${experiment}"

minSimNo=1
# maxSimNo=10
maxSimNo=1
nList=(100)
mList=(40)
# sList=(4 7)
sList=(7)
vafList=(0.05)
covList=(2000)
# kList=(0 1 2)
kList=(2)
# fnList=(0.15 0.25)
fnList=(0.15)
fpList=(0.0001)
naList=(0.15)
# appList=(ilp z3 openwbo)
appList=(ilp z3 openwbo)
declare -A cmdEXE
cmdEXE["ilp"]="python ${currDir}/../src/ilp/big_brother.py"
cmdEXE["z3"]="python ${currDir}/../src/csp_z3/main.py"
cmdEXE["openwbo"]="${currDir}/../src/csp_maxsat/csp_maxsat"

for n in ${nList[@]}; do
 for m in ${mList[@]}; do
  for s in ${sList[@]}; do	
   for vaf in ${vafList[@]}; do
    for cov in ${covList[@]}; do
     for k in ${kList[@]}; do
      for fn in ${fnList[@]}; do
       for fp in ${fpList[@]}; do
        for na in ${naList[@]}; do
         for app in ${appList[@]}; do
          for sim in $(seq ${minSimNo} ${maxSimNo}); do
           outDir="${outPre}/${app}"
           jobDir="${outPre}/job_${app}"
           mkdir -p ${jobDir}
           # rm ${jobDir}/${filePre}.out
           filePre="simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}"
           inFileFull=${dataDir}/noisy/${filePre}.SCnoisy
           fnW=1
           # fpW=`echo "$fn / $fp" | bc`
           fpW=33
           colW=20
           # create the qsub file
           echo "#!/bin/bash" > ${jobDir}/${filePre}.qsub
           echo "" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -d ${currDir}" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -o ${jobDir}/${filePre}.out" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -j oe" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -m af" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -M haghshenas.e@gmail.com" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -l nodes=1:ppn=1,vmem=5gb,walltime=1:00:00" >> ${jobDir}/${filePre}.qsub
           echo "#PBS -N p=${app},i=${sim},s=${s},k=${k}" >> ${jobDir}/${filePre}.qsub
           echo "" >> ${jobDir}/${filePre}.qsub
           if [ "${app}" == ilp ]; then
            echo "module unload python/2.7.13" >> ${jobDir}/${filePre}.qsub
            echo 'export PATH="/N/u/ehaghshe/Carbonate/anaconda2/bin:${PATH}"' >> ${jobDir}/${filePre}.qsub
            echo 'export GRB_LICENSE_FILE="/N/soft/rhel6/gurobi/7.5/gurobi751/gurobi.lic"' >> ${jobDir}/${filePre}.qsub
            echo "${cmdEXE[${app}]} -f ${inFileFull} -n ${fnW} -p ${fpW} -m 3 -t 1 -o ${outDir}" >> ${jobDir}/${filePre}.qsub
           fi
           if [ "${app}" == z3 ]; then
            echo "${cmdEXE[${app}]} -f ${inFileFull} -n ${fnW} -p ${fpW} -m ${colW} -t 1 -o ${outDir}" >> ${jobDir}/${filePre}.qsub
           fi
           if [ "${app}" == openwbo ]; then
            echo "${cmdEXE[${app}]} -f ${inFileFull} -n ${fnW} -p ${fpW} -m ${colW} -t 1 -o ${outDir}" >> ${jobDir}/${filePre}.qsub
           fi
           qsub ${jobDir}/${filePre}.qsub
          done
         done
        done
       done
      done
     done
    done
   done
  done
 done
done
