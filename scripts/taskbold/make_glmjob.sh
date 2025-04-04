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
modellist=("alt" "hcp")
run_folder=$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
check_folder="${run_folder}/glmruns.${session}"
check_template="${run_folder}/template.glms"
#subj_list=${run_folder}/../../${session}_completed.tsv
#subset_n=$(cat ${run_folder}/../../${session}_completed.tsv | wc -l )
# config file
config_file=${run_folder}/../config.json
uv_proj_path=$(jq -r '.uv_proj.proj_dir' "$config_file")
scratchdir="/tmp"
outdir=/tmp/${USER}/hcp_glms
email="${USER}@umn.edu"
group=`groups|cut -d" " -f1`

echo "Starting... "
echo 
if [ ! -d ${check_folder} ] ; then
	echo "${check_folder} do not exist... creating"
	mkdir -p ${check_folder}
fi
 

# counter to create run numbers
k=0
ses_id=${session}

cat ${run_folder}/subj_ids.txt | while read line ; do 
#cat $subj_list | while read line ; do
	for mod in "${modellist[@]}" ; do
		subj_id="sub-${line}"

		sed -e "s|SUBJECTID|${subj_id}|g" -e "s|MODTYPE|${mod}|g" -e "s|SCRATCHDIR|${scratchdir}|g" -e "s|OUT|${outdir}|g" -e "s|UVPROJ|${uv_proj_path}|g" -e "s|SESID|${ses_id}|g" ${check_template} > ${check_folder}/run${k}
		k=$((k+1))
	done
done
chmod 775 -R ${check_folder}

