#!/bin/bash
#SBATCH --job-name=hcp_rlone
#SBATCH --array=1,2#1087%30 # total 1087 for mriqc and 1017 for fmriprep and 1008 for xcpd, task glm just 2, syn call per hcp and alt model
#SBATCH --time=12:00:00 # dont need more than 3hrs for FMRIPrep, 1hr others and 12hr task bold
#SBATCH --cpus-per-task=12 # keep at 4 unless task, then set to 12
#SBATCH --mem-per-cpu=2GB
#SBATCH -p russpold
# OUTPUTS
#SBATCH --output=logs/rclone.%A_%a.out
#SBATCH --error=logs/rclone.%A_%a.err
#SBATCH --mail-user=demidenm@stanford.edu
#SBATCH --mail-type=ALL

# load rclone
module load rclone

# Create logs directory if it doesn't exist
mkdir -p logs

# type and output dir

# Base output directory
proc_type=${1}
if [ -z "$1" ]; then
echo "Error: \$1 should be provided (e.g., 'mriqc', 'fmriprep', 'xcpd', or 'taskbold')"
exit 1
fi

base_out_dir="/oak/stanford/groups/russpold/data/hcp_youth/derivatives"

# Read subject IDs from file into array
curr_dir=${PWD}
readarray -t SUBJECTS < ${curr_dir}/${proc_type}_sub_list.txt

# Get the subject ID for this array task
SUBJECT_ID=${SUBJECTS[$SLURM_ARRAY_TASK_ID-1]}

echo "Processing type: $proc_type"
echo "Processing subject: $SUBJECT_ID"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"
echo "Job ID: $SLURM_JOB_ID"
echo "Started at: $(date)"

# Set paths based on processing type
if [ "$proc_type" == "fmriprep" ]; then
    # fmriprep paths
    out_dir="${base_out_dir}/fmriprep_v24_0_1"
    ses_id="ses-3T"
    
    echo "Copying fmriprep data for subject: $SUBJECT_ID"
    
    # Copy main fmriprep directory
    rclone copy \
        msi-s3:hcp-youth/derivatives/fmriprep_v24_0_1/${ses_id}/sub-$SUBJECT_ID/ \
        ${out_dir}/sub-$SUBJECT_ID/ \
        --progress \
        --transfers 4 \
        --checkers 4 \
        --checksum
    
    # Copy HTML report
    rclone copy \
        msi-s3:hcp-youth/derivatives/fmriprep_v24_0_1/${ses_id}/sub-$SUBJECT_ID.html \
        ${out_dir}/ \
        --progress \
        --transfers 1 \
        --checkers 1 \
        --checksum
    
    # Copy FreeSurfer data
    rclone copy \
        msi-s3:hcp-youth/derivatives/fmriprep_v24_0_1/${ses_id}/sourcedata/freesurfer/sub-$SUBJECT_ID/ \
        ${out_dir}/sourcedata/freesurfer/sub-$SUBJECT_ID/ \
        --progress \
        --transfers 4 \
        --checkers 4 \
        --checksum

elif [ "$proc_type" == "mriqc" ]; then
    # mriqc paths
    out_dir="${base_out_dir}/mriqc_v23_1_0"
    
    echo "Copying mriqc data for subject: $SUBJECT_ID"
    
    # Copy mriqc directory
    rclone copy \
        msi-s3:hcp-youth/derivatives/mriqc_v23_1_0/ses-3T/sub-$SUBJECT_ID/ \
        ${out_dir}/sub-$SUBJECT_ID/ \
        --progress \
        --transfers 4 \
        --checkers 4 \
        --checksum

elif [ "$proc_type" == "xcpd" ]; then
    # XCP-D paths
    out_dir="${base_out_dir}/xcpd_v0_9_0"
    ses_id="ses-3T"
    
    echo "Copying XCP-D data for subject: $SUBJECT_ID"
    
    # Copy main XCP-D directory
    rclone copy \
        msi-s3:hcp-youth/derivatives/xcpd_v0_9_0/${ses_id}/sub-$SUBJECT_ID/ \
        ${out_dir}/sub-$SUBJECT_ID/ \
        --progress \
        --transfers 4 \
        --checkers 4 \
        --checksum
    
    # Copy HTML report
    rclone copy \
        msi-s3:hcp-youth/derivatives/xcpd_v0_9_0/${ses_id}/sub-$SUBJECT_ID.html \
        ${out_dir}/ \
        --progress \
        --transfers 1 \
        --checkers 1 \
        --checksum

elif [ "$proc_type" == "taskbold" ]; then
    # Task GLM paths
    out_dir="${base_out_dir}/node-taskglms_${SUBJECT_ID}"
    ses_id="ses-3T"
    
    echo "Copying task GLM data for MODEL: $SUBJECT_ID"
    
    # Define the subfolder types within alt and hcp
    subfolders=("firstlvl" "fixedeff" "vifs")
    
    # Copy alt subfolders
    for subfolder in "${subfolders[@]}"; do
        echo "Copying ${subfolder} data..."
        rclone copy \
            msi-s3:hcp-youth/derivatives/task_glms/${ses_id}/${SUBJECT_ID}/${subfolder}/ \
            ${out_dir}/${ses_id}/${subfolder}/ \
            --progress \
            --transfers 12 \
            --checkers 12 \
            --checksum
    done
    
else
    echo "Error: Invalid processing type '$proc_type'. Must be 'mriqc', 'fmriprep', 'xcpd', or 'taskbold'"
    exit 1
fi

echo "Completed at: $(date)"
