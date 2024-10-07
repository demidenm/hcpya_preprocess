#!/bin/bash
# This script automates the creation of run files for MRI preprocessing tools (mriqc or fmriprep).
# It reads configuration details from a JSON file and generates customized run files for each subject 
# in a subject list, with paths and other parameters based on user input and config data.

config_file="./config.json"  # Path to the JSON configuration file

# Check if config file exists
if [[ ! -f "$config_file" ]]; then
    echo "Config file $config_file not found! Exiting."
    exit 1
fi

# Ask the user to choose between mriqc or fmriprep preprocessing tools
echo "Please choose either 'mriqc' or 'fmriprep' for preprocessing."
read -r preproc

# Validate user input for preprocessing tool choice
preproc=$(echo "$preproc" | xargs)  # Trim leading/trailing spaces

if [[ "$preproc" == "mriqc" ]]; then
    # Load MRIQC specific settings from JSON
    config=$(jq -r '.mriqc' "$config_file")
elif [[ "$preproc" == "fmriprep" ]]; then
    # Load fMRIPrep specific settings from JSON
    config=$(jq -r '.fmriprep' "$config_file")
else
    echo "Invalid option. Should be 'mriqc' or 'fmriprep'. Provided: '$preproc'. Exiting."
    exit 1
fi

echo "Preprocessing option selected: ${preproc}."


# Extract various configuration variables from the JSON file
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

# Confirm the details with the user
echo
echo "You are generating run files for session: ${session} using the subject list in ${sub_file}."
echo "Input data will be sourced from NGDR path (${path_ngdr}) or S3 bucket (${path_s3bucket_in})."
echo "Selected sync option for input data: ${ngdr_or_s3}."
echo "Output files will be synced to S3 bucket: ${path_s3bucket_out}."
echo "Do you wish to continue? (yes = 1, no = 0)"
read -r yes_proc

# Exit if the user doesn't confirm
if [[ "$yes_proc" != "1" ]]; then
    echo "User declined... Exiting..."
    exit 1
fi

# Set output directories and variables for run files
scratch_dir="${scratch_dir}/${version}_out"  # Temporary data output directory
curr_folder="$(pwd)/${preproc}"  # Current working directory for the selected preprocessing option
sub_list="$(pwd)/subj_lists/${preproc}/${sub_file}"  # Subject list file path
run_folder="${curr_folder}/run_files.${version}_${session}"  # Folder for generated run files
preproc_template="template.${preproc}"  # Template file for generating run files

# Create the run folder if it doesn't already exist
if [[ ! -d "${run_folder}" ]]; then
    echo "${run_folder} does not exist... creating."
    mkdir -p "${run_folder}"
fi

if [[ ! -d "${curr_folder}/${preproc}_${session}_logs" ]]; then
    echo "${curr_folder}/${preproc}_${session}_logs does not exist... creating."
    mkdir -p "${curr_folder}/${preproc}_${session}_logs"
fi


# Initialize counter for creating run file numbers
k=0
ses_id="${session}"

# Loop through each subject ID in the subject list and create a run file for each
cat "$sub_list" | while read -r line; do
    subj_id=$(echo "$line" | awk '{print $1}')  # Extract the subject ID from the line
    
    # Create a run file for the subject by replacing placeholders in the template with actual values
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
        -e "s|LOGNUM|${k}|g" "${curr_folder}/${preproc_template}" > "${run_folder}/run${k}"
    
    # Increment counter
    k=$((k+1))
done

# Set appropriate permissions for the run folder
chmod 775 -R "${run_folder}"

echo "Run files created successfully in ${run_folder}."

