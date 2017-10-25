#!/bin/bash

dataDir="../data/simulated/21oct"
outPre="results/results_21oct_noColElim"

# timeLimit=3600
timeLimit=600

maxSimNo=10
# maxSimNo=1
nList=(100)
mList=(40)
sList=(4 7)
# sList=(7)
vafList=(0.05)
covList=(2000)
# kList=(0 1 2)
kList=(0)
fnList=(0.15 0.25)
# fnList=(0.15)
fpList=(0.0001)
naList=(0.15)
# appList=(ilp z3 openwbo)
appList=(ilp)
declare -A cmdEXE
cmdEXE["ilp"]="python ../src/ilp/big_brother.py"
cmdEXE["z3"]="python ../src/csp_z3/main.py"
cmdEXE["openwbo"]="../src/csp_maxsat/csp_maxsat -s /home/ehaghshe/Desktop/projects/intraTumor-minFlip/soft/open-wbo/open-wbo_static"
cmdEXE["qmaxsat"]="../src/csp_maxsat/csp_maxsat -s /home/ehaghshe/Desktop/projects/intraTumor-minFlip/soft/qMaxSAT/qmaxsat14.04auto-glucose3_static"

# for n in ${nList[@]}; do
#  for m in ${mList[@]}; do
#   for s in ${sList[@]}; do	
#    for vaf in ${vafList[@]}; do
#     for cov in ${covList[@]}; do
#      for k in ${kList[@]}; do
#       for fn in ${fnList[@]}; do
#        for fp in ${fpList[@]}; do
#         for na in ${naList[@]}; do
#          for app in ${appList[@]}; do
#           for sim in $(seq 1 ${maxSimNo}); do
#            fpN=1
#            fpW=`echo "$fn / $fp" | bc`
#            inFile=simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}.SCnoisy
#            inFileFull=${dataDir}/noisy/${inFile}
#            # ls ${inFileFull}
#            OPT="-f ${inFileFull} -n ${fpN} -p ${fpW} -m 0 -t 1 -o ${outPre}/${app}"
#            >&2 printf "${inFile} ${app} "
#            /usr/bin/time -f "time %e memory %M status %x" timeout ${timeLimit} ${cmdEXE[${app}]} ${OPT} 1> /dev/null
#           done
#          done
#         done
#        done
#       done
#      done
#     done
#    done
#   done
#  done
# done

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
          for sim in $(seq 1 5); do
           fpN=1
           fpW=`echo "$fn / $fp" | bc`
           inFile=simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}.SCnoisy
           inFileFull=${dataDir}/noisy/${inFile}
           # ls ${inFileFull}
           OPT="-f ${inFileFull} -n ${fpN} -p ${fpW} -m 0 -t 1 -o ${outPre}/${app}"
           timeout ${timeLimit} ${cmdEXE[${app}]} ${OPT} 1> /dev/null &
          done
          wait
          for sim in $(seq 6 10); do
           fpN=1
           fpW=`echo "$fn / $fp" | bc`
           inFile=simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}.SCnoisy
           inFileFull=${dataDir}/noisy/${inFile}
           # ls ${inFileFull}
           OPT="-f ${inFileFull} -n ${fpN} -p ${fpW} -m 0 -t 1 -o ${outPre}/${app}"
           timeout ${timeLimit} ${cmdEXE[${app}]} ${OPT} 1> /dev/null &
          done
          wait
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
