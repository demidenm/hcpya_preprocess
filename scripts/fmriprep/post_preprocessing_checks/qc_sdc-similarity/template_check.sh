#!/bin/bash
curr_dir=`pwd`
sub=SUBJECT
ses=SESSION 
type=dice
roi_path=/home/feczk001/mdemiden/slurm_ABCD_s3/hcpya_preprocess/scripts/fmriprep/post_preprocessing_checks/qc_sdc-similarity/roi_mask/leftvisual.nii.gz
fmriprep_vr=fmriprep_v24_0_1
tmp=/scratch.local/${USER}/similarity_check
out_dir=${tmp}/peristim/
out_sim=${curr_dir}/tmp/sub-${sub}_${ses}_check-html-similarity.tsv
main_sim=${curr_dir}/../${ses}_check-html-similarity.tsv
out_peristim=${curr_dir}/tmp/sub-${sub}_${ses}_check-peristim.tsv
main_peristim=${curr_dir}/../${ses}_check-peristim.tsv
s3_bucket="s3://hcp-youth" # store fmriprep here
s3_raw="s3://HCP_YA/BIDS" # input bids data

# if file exists,  remove row of matching ID to not have redundant content
if [ -f "${ses}_check-html-similarity.tsv" ]; then
	sed -i "/${sub}/d" "${ses}_check-html-similarity.tsv"
fi

# set director; and copy down from s3 and nda folder; get number of fieldmaps (using AP only here)
mkdir -p ${tmp}
s3cmd sync --recursive ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sub-${sub} ${tmp}/ --exclude "*goodvoxels*" --exclude "*91k*" --exclude "*.gii" --exclude "*.json" --exclude "*_boldref.nii.gz" --exclude "*_xfm.txt"
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
	nii_file=$(ls ${base}*_bold.nii.gz 2>/dev/null | head -n 1)  # Find matching bold file
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
for event_file in ` ls ${tmp}/sub-${sub}/ses-${ses}/func/sub-${sub}_ses-${ses}_task-motor_*_run-*_events.tsv ` ; do
	s3cmd put $event_file ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sourcedata/event_files/sub-${sub}/ses-${ses}/func/
done

# extract html contents 
bold_runs=$(cat ${tmp}/sub-${sub}.html | grep -E '<h2 class="sub-report-group mt-4">Reports for: session <span class="bids-entity">'"$ses"'</span>, task' | awk -F'[<>]' '{ print $9,$17 }')
sdc_runs=$(cat ${tmp}/sub-${sub}.html | grep "distortion correction:" | awk -F" " '{ print $4}')

# set subject session in folder
sess_inp=${tmp}/sub-${sub}/ses-${ses}

num=0
echo "$bold_runs" | while read run ; do 
	((num++))
	sdc_type=$(echo "$sdc_runs" | sed -n "${num}p")
	task=$(echo $run | awk -F" " '{ print $1 }')
	run=$(echo $run | awk -F" " '{ print $2 }')

	# Determine if events exist
	if ls ${tmp}/sub-${sub}/ses-${ses}/func/sub-${sub}_ses-${ses}_task-${task}_*_run-${run}_events.tsv 1> /dev/null 2>&1; then
		events_exist="Exists"
	else
		events_exist="None"
	fi

	# Default to run 01 if empty
	if [ -z "$run" ]; then
		run="01"
		echo "${num}. Calculating similarity for sub-${sub}, task-${task}, run empty, defaulting to run-${run}"
	else
		echo "${num}. Calculating similarity for sub-${sub}, task-${task}, run-${run}"
	fi

	# RUN PYTHON CODE TO EXTRACT SIMILARITY ESTIMATES
	sim_out=$(python ${curr_dir}/../similarity_check.py --in_dat ${sess_inp} --task ${task} ${run:+--run $run} --stype ${type}) 2>&1
	sim_error=$?

	if [ ${sim_error} -eq 0 ]; then
		echo "Python Similarity ( $task $run ) estimate completed successfully!"
		vals=($sim_out)
		echo -e "${sub}\t${ses}\t${task}\t${run}\t${events_exist}\t${sdc_type}\t${vals[0]}\t${vals[1]}" >> ${out_sim}
		echo "Stimilarity finished Successfully"

	else
		echo "Python Similarity ( $task $run ) failed."
		exit 1
	fi
done

cat $out_sim >> $main_sim
rm $out_sim


# RUN PYTHON TO EXTRA PERISTIMULUS DATA ONLY FOR MOTOR TASK
motor_exist=$(ls ${tmp}/sub-${sub}/ses-${ses}/func/sub-${sub}_ses-${ses}_task-motor_dir-*_run-*_bold.nii.gz 2>/dev/null )
num_files=$(echo "$motor_exist" | wc -l)

if [ "$num_files" -ge 2 ]; then
	mkdir -p ${out_dir}/sub-${sub}/ses-${ses}/func
	peristim_out=$(python ${curr_dir}/../create_peristim.py --in_dir ${tmp} --sub_id ${sub} --task "motor" --roi_mask ${roi_path} --out_path "${out_dir}/sub-${sub}/ses-${ses}/func" ) 2>&1
	peristim_error=$?

	if [ ${peristim_error} -eq 0 ]; then
		echo "Python Peristimulus estimate completed successfully!"
		perivals=($peristim_out)
		echo -e "${sub}\t${ses}\tmotor\tleft_visual\t${perivals[0]}\t${perivals[1]}\t${perivals[2]}" >> ${out_peristim}
		s3cmd --recursive put ${out_dir}/sub-${sub}/ses-${ses}/func/*_timeseries-roi.tsv ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sourcedata/out_files/sub-${sub}/ses-${ses}/func/
		s3cmd --recursive put ${out_dir}/sub-${sub}/ses-${ses}/func/*_plot-peristim.png ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sourcedata/out_files/sub-${sub}/ses-${ses}/func/
		echo "Peristim finished Successfully" 
		cat $out_peristim >> $main_peristim
		rm $out_peristim
	else
		echo "Python Peristimulus failed."
		exit 1
	fi
else
	echo "Subject ${sub} doesnt have motor task"

fi


echo "QC Runs Finished Successfully"
