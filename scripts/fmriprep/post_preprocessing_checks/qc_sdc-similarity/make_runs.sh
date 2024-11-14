#!/bin/bash 

echo "Please choose a session value 3T or 7T:"
read ses

if [ -n "${ses}" ]; then
    if [[ "$ses" == "3T" || "$ses" == "7T" ]]; then
        echo "${ses} chosen as ses, continuing."
    else
        echo
        echo "should be 3T or 7T, provided ${ses}. Exiting."
        echo
        exit 1
    fi

else
        echo
        echo "Variable is empty, expected string. Exiting"
        echo
        exit 1

fi


set +x 
# determine data directory, run folders, and run templates
session=${ses}
run_folder=`pwd`
check_folder="${run_folder}/run_files.${session}"
check_template="${run_folder}/template_check.sh"
#subj_list=${run_folder}/subject_list/${session}_ids.txt
subj_list=${run_folder}/../../${session}_completed.tsv
subset_n=1013

email=`echo $USER@umn.edu`
group=`groups|cut -d" " -f1`

echo "Starting... "
echo 
if [ ! -d ${check_folder} ] ; then
	echo "${check_folder} do not exist... creating"
	mkdir -p ${check_folder}/tmp
fi
 

# counter to create run numbers
k=0
ses_id=${session}

cat $subj_list | head -n $subset_n | while read line ; do 
#cat $subj_list | while read line ; do
	subj_id=`echo $line | awk -F' ' '{ print $1 }'`

	sed -e "s|SUBJECT|${subj_id}|g" -e "s|SESSION|${ses_id}|g" ${check_template} > ${check_folder}/run${k}
	k=$((k+1))
done

chmod 775 -R ${check_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_check.sh 

