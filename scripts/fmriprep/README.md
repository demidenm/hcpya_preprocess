# ABCD-BIDS: FMRIPrep Preprocessing Pipeline

This code is to rerun fMRIPrep preprocessing. The general overview:

- template.fmriprep
    - This is the template used to copy data to a tmp area to preprocess locally. It also includes the singularity run for fMRIPrep + the sync to s3
- resources_*.sh 
    - This is your research request for each fMRIPrep job that is submitted to slurm (takes 4-7hrs each)
- submit_*.sh 
    - jobs are submitted using arrays indicating the runs in `run_files.*` folder
    - to submit the first 100 subjs for independent slurm jobs use: ./submit_fmriprep.sh 0-100

The `task_list.json` specifies which tasks to run/filter using [BIDS filter file tag](https://fmriprep.org/en/stable/usage.html#:~:text=a%20multiecho%20series-,%2D%2Dbids%2Dfilter%2Dfile,-A%20JSON%20file)

The singularity run is currently templated as:

```bash
singularity run --cleanenv \
    -B "${bids_dir}:/bids_dir" \
    -B "${data_dir}/processed/${fmriprep_ver}/sub-${subj_id}_ses-${ses_id}:/output_dir" \
    -B "${data_dir}/work_dir/${fmriprep_ver}/sub-${subj_id}_ses-${ses_id}:/wd" \
    -B "${freesurfer_license}:/freesurf_license.txt" \
    "${singularity_img}" \
    /bids_dir /output_dir participant \
    --participant-label "${subj_id}" \
    --fs-license-file /freesurf_license.txt \
    --ignore slicetiming \
    --fd-spike-threshold .5 \
    --output-space MNI152NLin2009cAsym:res-2 \
    --cifti-output 91k \
    -vv \
    -w /wd
```