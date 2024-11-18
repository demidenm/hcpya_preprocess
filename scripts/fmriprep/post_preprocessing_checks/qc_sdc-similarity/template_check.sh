#!/bin/bash
curr_dir=`pwd`
sub=SUBJECT
ses=SESSION 
type=dice
nda_dir=/spaces/ngdr/ref-data/abcd/nda-3165-2020-09
fmriprep_vr=fmriprep_v24_0_1
tmp=/scratch.local/${USER}/similarity_check
out_file=${curr_dir}/tmp/sub-${sub}_${ses}_check-html-similarity.tsv
main_file=${curr_dir}/../${ses}_check-html-similarity.tsv
s3_bucket="s3://hcp-youth" # store fmriprep here
s3_raw="s3://HCP_YA/BIDS" # input bids data

# if file exists,  remove occurs of ID to not have redundant content
if [ -f "${ses}_check-html-similarity.tsv" ]; then
	sed -i "/${sub}/d" "${ses}_check-html-similarity.tsv"
fi

# set director; and copy down from s3 and nda folder; get number of fieldmaps (using AP only here)
mkdir -p ${tmp}
s3cmd sync --recursive ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sub-${sub} ${tmp}/ --exclude "*goodvoxels*" --exclude "*91k*" --exclude "*.gii" --exclude "*.json" --exclude "*desc-preproc_bold.nii.gz"
s3cmd sync ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sourcedata/freesurfer/sub-${sub}/mri/brain.mgz ${tmp}/sub-${sub}/ses-${ses}/anat/

# convert fressurfer brain to .nii.gz, bin image, resample to brain-mask.nii.gz
cd ${tmp}/sub-${sub}/ses-${ses}/anat/
file=$(ls *_desc-brain_mask.nii.gz | grep -v "MNI152") # exclude MNI152 brain mask
mri_convert brain.mgz fs_brain.nii.gz

# T1w.nii.gz; sometimes multile T1ws, so only taking the first one
first_nii=$(s3cmd ls ${s3_raw}/sub-${sub}/ses-${ses}/anat/ | grep "T1w" | grep "\.nii" | head -n 1 | awk '{print $4}')
first_json=$(s3cmd ls ${s3_raw}/sub-${sub}/ses-${ses}/anat/ | grep "T1w" | grep "\.json" | head -n 1 | awk '{print $4}')

s3cmd get "$first_nii" ${tmp}/sub-${sub}/ses-${ses}/anat/
s3cmd get "$first_json" ${tmp}/sub-${sub}/ses-${ses}/anat/

# sync all events files to ensure matching files exists per task/run
s3cmd sync --recursive --include="*_events.tsv" ${s3_raw}/sub-${sub}/ses-${ses}/func/ ${tmp}/sub-${sub}/ses-${ses}/func/

# rename the events files to match by RUN with BOLD
for tsv in ${tmp}/sub-${sub}/ses-${ses}/func/*_events.tsv; do
	base="${tsv%_events.tsv}"  # Remove "_events.tsv" suffix
	nii_file=$(ls ${base}*_bold.nii.gz 2>/dev/null)  # Find matching bold file
	if [[ -n $nii_file ]]; then  # Check if the bold file exists
		run=$(echo "$nii_file" | grep -o "_run-[0-9]_")  # Extract _run-<number>_
		if [[ -n $run ]]; then
			new_tsv="${base}${run}events.tsv"  # Construct new filename
			mv "$tsv" "$new_tsv"  # Rename the file
			echo "Renamed: $tsv -> $new_tsv"
		else
			echo "No run information found in: $nii_file"
		fi
	else	
		echo "No matching bold file found for: $tsv"
	fi
done

# sync events files to s3 fmriprep sourcedata folder
s3cmd --recursive put ${tmp}/sub-${sub}/ses-${ses}/func/*_events.tsv ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sourcedata/events_files/sub-${sub}/ses-${ses}/func/

# extract html contents 
bold_runs=$(cat ${tmp}/sub-${sub}.html | grep -E '<h2 class="sub-report-group mt-4">Reports for: session <span class="bids-entity">'"$ses"'</span>, task' | awk -F'[<>]' '{ print $9,$17 }')
sdc_runs=$(cat ${tmp}/sub-${sub}.html | grep "distortion correction:" | awk -F" " '{ print $4}')

# set subject session in folder
sess_inp=${tmp}/sub-${sub}/ses-${ses}

# extract and save
num=0
echo "$bold_runs" | while read run ; do 
	((num++))
	sdc_type=$(echo "$sdc_runs" | sed -n "${num}p")
	task=$(echo $run | awk -F" " '{ print $1 }')
	run=$(echo $run | awk -F" " '{ print $2 }')
        
	if ls ${tmp}/sub-${sub}/ses-${ses}/func/sub-${sub}_ses-${ses}_task-${task}_*_run-${run}_events.tsv 1> /dev/null 2>&1; then
                events_exist="Exists"
        else
            	events_exist="None"
        fi

	# RUN PYTHON CODE TO EXTRACT SIMILARITY ESTIMATES
	if [ -n "$run" ]; then
		echo "${num}. Calculating similarity for sub-${sub}, task-${task}, run-${run} "
		output=$(python ${curr_dir}/../similarity_check.py --in_dat ${sess_inp} --task ${task} --run ${run} --stype ${type} )
        	sim_error=$?

        	if [ ${sim_error} -eq 0 ]; then
                	echo "Python Similarity ( $task $run ) estimate completed successfully!"
			vals=($output)
                	echo -e "${sub}\t${ses}\t${task}\t${run}\t${events_exist}\t${sdc_type}\t${vals[0]}\t${vals[1]}" >> ${out_file}
        	else
            		echo "Python Similarity ( $task $run ) failed."
                	exit 1
        	fi
	else
		echo "${num}. Calculating similarity for sub-${sub}, task-${task}, run empty, 1-run "
		output=$(python ${curr_dir}/../similarity_check.py --in_dat ${sess_inp} --task ${task} --stype ${type})
                sim_error=$?

                if [ ${sim_error} -eq 0 ]; then
                        echo "Python Similarity ( $task empty run ) estimate completed successfully!"
                        run=01
			vals=($output)
                        echo -e "${sub}\t${ses}\t${task}\t${run}\t${events_exist}\t${sdc_type}\t${vals[0]}\t${vals[1]}" >> ${out_file}
		else
                        echo "Python Similarity ( $task empty run ) failed."
                        exit 1
                fi
	fi
done

cat $out_file >> $main_file
rm $out_file

echo "Finished Successfully"
