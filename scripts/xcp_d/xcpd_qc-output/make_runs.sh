#!/bin/bash 

echo "Assuming session is 3T"
session=3T
run_folder=`pwd`
check_folder=${run_folder}/run_files.${session}
check_template=${run_folder}/template.xcp_d
subj_list=${run_folder}/../${session}_completed.tsv
subset_n=$(cat $subj_list | wc -l )

echo "Starting... "
echo 
if [ ! -d ${check_folder} ] ; then
	echo "${check_folder} do not exist... creating"
	mkdir -p ${check_folder}/tmp
fi

k=0

cat $subj_list | head -n $subset_n | while read line ; do 
	subj_id=`echo $line | awk -F' ' '{ print $1 }'`
	sed -e "s|SUBJECT|${subj_id}|g" -e "s|CURR_DIR|${run_folder}|g" ${check_template} > ${check_folder}/run${k}
	k=$((k+1))
done

chmod 775 -R ${check_folder}
