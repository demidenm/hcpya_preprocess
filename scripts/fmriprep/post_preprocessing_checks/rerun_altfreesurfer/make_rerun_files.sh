#!/bin/bash 

echo "Please choose a value baselineYear1Arm1 or 2YearFollowUpYArm1:"
read ses

if [ -n "${ses}" ]; then
    if [[ "$ses" == "baselineYear1Arm1" || "$ses" == "2YearFollowUpYArm1" ]]; then
        echo "${ses} chosen as ses, continuing."
    else
        echo
        echo "should be baselineYear1Arm1 or 2YearFollowUpYArm1, provided ${ses}. Exiting."
        echo
        exit 1
    fi

else
        echo
        echo "Variable is empty, expected: baselineYear1Arm1 or 2YearFollowUpYArm1. Exiting"
        echo
        exit 1

fi

set +x 
# determine data directory, run folders, and run templates
session=${ses}
fmriprep_ver=fmriprep_v23_1_4
data_dir="/scratch.local/$USER/${fmriprep_ver}_out" # where to output data
data_input="/spaces/ngdr/ref-data/abcd/nda-3165-2020-09/" # data that BIDS data will be pulled from
#data_bucket="s3://ABCD_BIDS" # bucket to input data onto s3, preprocessed output pushed to
data_bucket="s3://abcd-mriqc-fmriprep"
run_folder=`pwd`
fmriprep_folder="${run_folder}/rerunfiles.${fmriprep_ver}_${session}"
fmriprep_template="template.${fmriprep_ver}_rerun_freesurfer"
subj_list=${run_folder}/rerun_fmriprep_${session}_subjs.txt

email=`echo $USER@umn.edu`
group=`groups|cut -d" " -f1`

echo "Starting... "
echo 
if [ ! -d ${fmriprep_folder} ] ; then
	echo "${fmriprep_folder} do not exist... creating"
	mkdir ${fmriprep_folder}
fi
 

# counter to create run numbers
k=0
ses_id=${session}

cat $subj_list | while read line ; do 
	subj_id=`echo $line | awk -F' ' '{print $1 }'` # | awk -F'-' '{print $2}'`
	#ses_id=`echo $line | awk -F' ' '{print $2 }'` # | awk -F'-' '{print $2}'`

	sed -e "s|SUBJECTID|${subj_id}|g" -e "s|SESID|${ses_id}|g" -e "s|FMRIPREP|${fmriprep_ver}|g" -e "s|DATADIR|${data_dir}|g" -e "s|INPUT|${data_input}|g" -e "s|BUCKET|${data_bucket}|g" -e "s|RUNDIR|${run_folder}|g" -e "s|LOGNUM|${k}|g" ${run_folder}/${fmriprep_template} > ${fmriprep_folder}/run${k}
	k=$((k+1))
done

chmod 775 -R ${fmriprep_folder}

sed -e "s|GROUP|${group}|g" -e "s|EMAIL|${email}|g" -i ${run_folder}/resources_${fmriprep_ver}_rerun_${session}.sh 

