#!/bin/bash
curr_dir=`pwd`
sub=SUBJECT
ses=SESSION 
type=dice
nda_dir=/spaces/ngdr/ref-data/abcd/nda-3165-2020-09
fmriprep_vr=fmriprep_v23_1_4
tmp=/scratch.local/${USER}/similarity_check
out_file=${curr_dir}/tmp/sub-${sub}_${ses}_check-html-similarity.tsv
main_file=${curr_dir}/../${ses}_check-html-similarity.tsv

if [[ "$ses" == "baselineYear1Arm1" ]] ; then
        s3_bucket="s3://abcd-mriqc-fmriprep" # store Baseline here
elif [[ "$ses" == "2YearFollowUpYArm1" ]] ; then
        s3_bucket="s3://ABCD_BIDS" # Store 2Year here
else
    	echo "wrong session option"
        exit 1
fi


# set director; and copy down from s3 and nda folder; get number of fieldmaps (using AP only here)
mkdir -p ${tmp}
s3cmd sync --recursive ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sub-${sub} ${tmp}/ --exclude "*goodvoxels*" --exclude "*91k*" --exclude "*.gii" --exclude "*.json"
s3cmd sync ${s3_bucket}/derivatives/${fmriprep_vr}/ses-${ses}/sourcedata/freesurfer/sub-${sub}/mri/brain.mgz ${tmp}/sub-${sub}/ses-${ses}/anat/

# convert fressurfer brain to .nii.gz, bin image, resample to brain-mask.nii.gz
cd ${tmp}/sub-${sub}/ses-${ses}/anat/
file=$(ls *_desc-brain_mask.nii.gz | grep -v "MNI152") # exclude MNI152 brain mask
mri_convert brain.mgz fs_brain.nii.gz

# copy first run anat or T1w.nii.gz; sometimes multile T1ws, using run-01 to avoid affine error in dice calc
if [ -e ${nda_dir}/sub-${sub}/ses-${ses}/anat/*_run-01_T1w.nii.gz ] ; then
	cp ${nda_dir}/sub-${sub}/ses-${ses}/anat/*_run-01_T1w.nii.gz ${tmp}/sub-${sub}/ses-${ses}/anat/
else
	cp ${nda_dir}/sub-${sub}/ses-${ses}/anat/*_T1w.nii.gz ${tmp}/sub-${sub}/ses-${ses}/anat/
fi


# if fmap exists, check AP num
if [ -d "${nda_dir}/sub-${sub}/ses-${ses}/fmap/" ]; then
	num_ap_fm=$(ls "${nda_dir}/sub-${sub}/ses-${ses}/fmap/"*-AP*epi.nii.gz | wc -l)
else
	num_ap_fm=0
fi

# extract html contents 
bold_runs=$(cat ${tmp}/sub-${sub}.html | grep -E '<h2 class="sub-report-group">Reports for: session <span class="bids-entity">'"$ses"'</span>, task' | awk -F'[<>]' '{ print $9,$13 }')
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

	# RUN PYTHON CODE TO EXTRACT SIMILARITY ESTIMATES
	if [ -n "$run" ]; then
		echo "${num}. Calculating similarity for sub-${sub}, task-${task}, run-${run} "
		output=$(python ${curr_dir}/../similarity_check.py --in_dat ${sess_inp} --task ${task} --run ${run} --stype ${type} )
        	sim_error=$?

        	if [ ${sim_error} -eq 0 ]; then
                	echo "Python Similarity ( $task $run ) estimate completed successfully!"
			vals=($output)
                	echo -e "${sub}\t${ses}\t${task}\t${run}\t${sdc_type}\t${num_ap_fm}\t${vals[0]}\t${vals[1]}\t${vals[2]}\t${vals[3]}\t${vals[4]}" >> ${out_file}
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
                        echo -e "${sub}\t${ses}\t${task}\t${run}\t${sdc_type}\t${num_ap_fm}\t${vals[0]}\t${vals[1]}\t${vals[2]}\t${vals[3]}\t${vals[4]}" >> ${out_file}
		else
                        echo "Python Similarity ( $task empty run ) failed."
                        exit 1
                fi

	fi
done

cat $out_file >> $main_file
rm $out_file

echo "Finished Successfully"