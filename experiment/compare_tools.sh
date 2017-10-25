#!/bin/bash

resDir="results/results_21oct_noColElim"
conflictEXE="/home/ehaghshe/Desktop/projects/intraTumor-minFlip/code/csp_maxsat/findConflicts"

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

# # check conflict free
# echo "check conflict free"
# for n in ${nList[@]}; do
#  for m in ${mList[@]}; do
#   for s in ${sList[@]}; do  
#    for vaf in ${vafList[@]}; do
#     for cov in ${covList[@]}; do
#      for k in ${kList[@]}; do
#       for fn in ${fnList[@]}; do
#        for fp in ${fpList[@]}; do
#         for na in ${naList[@]}; do
#          for sim in $(seq 1 ${maxSimNo}); do
#           for app in ${appList[@]}; do
#            filePrefix=simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}
#            outFile=${resDir}/${app}/${filePrefix}.output
#            logFile=${resDir}/${app}/${filePrefix}.log
#            if [ ! -f ${logFile} ] || [ ! -f ${outFile} ]; then
#             echo "[WARNING] n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} sim:${sim} app:${app} failed!"
#             continue
#            fi
#            # 
#            ${conflictEXE} outFile
#            if [ ! $? -eq 0 ]; then
#             echo "[ERROR] n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} sim:${sim} app:${app} not conflict free"
#            fi
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

# echo ""
# echo ""
# echo ""

# # check number of flips
# echo "check number of flips"
# for n in ${nList[@]}; do
#  for m in ${mList[@]}; do
#   for s in ${sList[@]}; do  
#    for vaf in ${vafList[@]}; do
#     for cov in ${covList[@]}; do
#      for k in ${kList[@]}; do
#       for fn in ${fnList[@]}; do
#        for fp in ${fpList[@]}; do
#         for na in ${naList[@]}; do
#          for sim in $(seq 1 ${maxSimNo}); do
#           declare -A numFlip01
#           declare -A numFlip10
#           for app in ${appList[@]}; do
#            filePrefix=simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}
#            outFile=${resDir}/${app}/${filePrefix}.output
#            logFile=${resDir}/${app}/${filePrefix}.log
#            if [ ! -f ${logFile} ] || [ ! -f ${outFile} ]; then
#             echo "[WARNING] n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} sim:${sim} app:${app} failed!"
#             numFlip01["${app}"]=0
#             numFlip10["${app}"]=0
#             continue
#            fi
#            # 
#            numFlip01["${app}"]=`cat ${logFile} | grep "0_1_FLIPS_REPORTED" | awk '{print $2}'`
#            numFlip10["${app}"]=`cat ${logFile} | grep "1_0_FLIPS_REPORTED" | awk '{print $2}'`
#           done
#           #
#           if [ ${numFlip01["ilp"]} != ${numFlip01["z3"]} ] || [ ${numFlip01["ilp"]} != ${numFlip01["openwbo"]} ]; then
#            echo "[ERROR] n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} sim:${sim} 0_1_FLIPS mismatch" ilp:${numFlip01["ilp"]} z3:${numFlip01["z3"]} openwbo:${numFlip01["openwbo"]}
#           fi
#           if [ ${numFlip10["ilp"]} != ${numFlip10["z3"]} ] || [ ${numFlip10["ilp"]} != ${numFlip10["openwbo"]} ]; then
#            echo "[ERROR] n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} sim:${sim} 1_0_FLIPS mismatch" ilp:${numFlip10["ilp"]} z3:${numFlip10["z3"]} openwbo:${numFlip10["openwbo"]}
#           fi
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

# echo ""
# echo ""
# echo ""

# Now calculate running times!
echo "calculating running times..."
for n in ${nList[@]}; do
 for m in ${mList[@]}; do
  for s in ${sList[@]}; do	
   for vaf in ${vafList[@]}; do
    for cov in ${covList[@]}; do
     for k in ${kList[@]}; do
      for fn in ${fnList[@]}; do
       for fp in ${fpList[@]}; do
        for na in ${naList[@]}; do
         declare -A runTime
         for app in ${appList[@]}; do
          sumTime=0
          # calculate things
          for sim in $(seq 1 ${maxSimNo}); do
           filePrefix=simNo_${sim}-n_${n}-m_${m}-s_${s}-minVAF_${vaf}-cov_${cov}-k_${k}-fn_${fn}-fp_${fp}-na_${na}
           outFile=${resDir}/${app}/${filePrefix}.output
           logFile=${resDir}/${app}/${filePrefix}.log
           # ls ${outFile}
           if [ ! -f ${logFile} ] || [ ! -f ${outFile} ]; then
            echo "[WARNING] n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} app:${app} sim:${sim} failed!"
            continue
           fi
           appTime=`cat ${logFile} | grep "MODEL_SOLVING_TIME_SECONDS" | awk '{print $2}'`
           sumTime=$(echo $sumTime+$appTime | bc )
          done
          #
          runTime["${app}"]=`echo "scale=2; $sumTime / $maxSimNo" | bc`
         done
         echo n:${n} m:${m} s:${s} vaf:${vaf} cov:${cov} k:${k} fn:${fn} fp:${fp} na:${na} ilpTime:${runTime["ilp"]} z3Time:${runTime["z3"]} openwboTime:${runTime["openwbo"]}
        done
       done
      done
     done
    done
   done
  done
 done
done
