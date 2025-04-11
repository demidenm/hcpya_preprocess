#!/bin/bash
# This script automates the creation of run files for MRI preprocessing tools.
# It reads configuration details from a JSON file and generates customized run files for each subject.

script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
config_file="${script_dir}/config.json"

# Check if config file exists
if [[ ! -f "$config_file" ]]; then
    echo "Config file $config_file not found! Exiting."
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq command not found. Please install it."
    exit 1
fi

# Ask the user to choose preprocessing tool
echo "Please choose either 'mriqc', 'fmriprep' or 'xcp_d' for preprocessing."
read -r preproc
preproc=$(echo "$preproc" | xargs)  # Trim spaces

# Validate preprocessing tool choice
valid_options=("mriqc" "fmriprep" "xcp_d")
valid_choice=0

for option in "${valid_options[@]}"; do
    if [[ "$preproc" == "$option" ]]; then
        valid_choice=1
        break
    fi
done

if [[ $valid_choice -eq 0 ]]; then
    echo "Invalid option. Should be 'mriqc', 'fmriprep' or 'xcp_d'. Provided: '$preproc'. Exiting."
    exit 1
fi

# Load specific settings from JSON
config=$(jq -r ".$preproc" "$config_file")
echo "Preprocessing option selected: ${preproc}."

# Extract configuration variables
ngdr_or_s3=$(echo "$config" | jq -r '.ngdr_or_s3bucket')
session=$(echo "$config" | jq -r '.ses')
path_ngdr=$(echo "$config" | jq -r '.path_ngdr')
path_s3bucket_in=$(echo "$config" | jq -r '.path_s3bucket_in')
path_s3bucket_out=$(echo "$config" | jq -r '.path_s3bucket_out')
version=$(echo "$config" | jq -r '.version')
scratch_dir=$(echo "$config" | jq -r '.scratch_dir')
sub_file=$(echo "$config" | jq -r '.sub_file')
usr_email=$(echo "$config" | jq -r '.usr_email')
sif_path=$(echo "$config" | jq -r '.sif_path')
freesurf_key=$(echo "$config" | jq -r '.freesurf_key')

# Confirm details with user
echo
echo "You are generating run files for session: ${session} using the subject list in ${sub_file}."
echo "Input data will be sourced from NGDR path (${path_ngdr}) or S3 bucket (${path_s3bucket_in})."
echo "Selected sync option for input data: ${ngdr_or_s3}."
echo "Output files will be synced to S3 bucket: ${path_s3bucket_out}."
echo "Do you wish to continue? (yes = 1, no = 0)"
read -r user_confirm

# Exit if user doesn't confirm
if [[ "$user_confirm" != "1" ]]; then
    echo "User declined... Exiting..."
    exit 1
fi

# Set output directories and variables for run files
scratch_dir="${scratch_dir}/${version}_out"
curr_folder="${script_dir}/${preproc}"
sub_list="${script_dir}/subj_lists/${preproc}/${sub_file}"
run_folder="${curr_folder}/run_files.${version}_${session}"
preproc_template="template.${preproc}"
template_path="${curr_folder}/${preproc_template}"

# Check if subject list file exists
if [[ ! -f "$sub_list" ]]; then
    echo "Subject list file not found at: $sub_list. Exiting."
    exit 1
fi

# Check if template file exists
if [[ ! -f "$template_path" ]]; then
    echo "Template file not found at: $template_path. Exiting."
    exit 1
fi

# Create required directories
for dir in "${run_folder}" "${curr_folder}/${preproc}_${session}_logs"; do
    if [[ ! -d "$dir" ]]; then
        echo "$dir does not exist... creating."
        mkdir -p "$dir"
    fi
done

# Initialize counter for run file numbers
file_counter=0
ses_id="${session}"

# Count total subjects for progress tracking
total_subjects=$(wc -l < "$sub_list")
echo "Processing $total_subjects subjects..."

# Process each subject
while read -r line; do
    subj_id=$(echo "$line" | awk '{print $1}')
    echo "Creating run file for subject $subj_id ($(($file_counter+1))/$total_subjects)"
    
    # Create a run file by replacing placeholders with actual values
    sed -e "s|SUBJECTID|${subj_id}|g" \
        -e "s|SESID|${ses_id}|g" \
        -e "s|S3ORNGDR|${ngdr_or_s3}|g" \
        -e "s|PREPROC_VR|${version}|g" \
        -e "s|SCRATCHDIR|${scratch_dir}|g" \
        -e "s|NGDR|${path_ngdr}|g" \
        -e "s|INBUCKET|${path_s3bucket_in}|g" \
        -e "s|OUTBUCKET|${path_s3bucket_out}|g" \
        -e "s|SIGINF|${sif_path}|g" \
        -e "s|FSLICENSE|${freesurf_key}|g" \
        -e "s|RUNDIR|${curr_folder}|g" \
        -e "s|LOGNUM|${file_counter}|g" "$template_path" > "${run_folder}/run${file_counter}"
    
    # Increment counter
    file_counter=$((file_counter+1))
done < "$sub_list"

# Set appropriate permissions for the run folder
chmod 775 -R "${run_folder}"

echo "Run files created successfully in ${run_folder}."