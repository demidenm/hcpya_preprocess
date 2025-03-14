#!/bin/bash

# Configuration
session="3T"
run_folder=$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
check_folder="${run_folder}/run_files.${session}"
check_template="${run_folder}/template.xcp_d"
subj_list="${run_folder}/../${session}_completed.tsv"
config_file="${run_folder}/../../config.json"
uv_proj_path=$(jq -r '.uv_proj.proj_dir' "$config_file")

# Get total subjects for processing
subset_n=$(wc -l < "$subj_list")

echo "Starting... "
echo "Assuming session is ${session}"

# Create output directory if needed
if [ ! -d "${check_folder}" ]; then
    echo "${check_folder} does not exist... creating"
    mkdir -p "${check_folder}/tmp"
fi

# Process each subject
k=0
cat "$subj_list" | head -n "$subset_n" | while read line; do 
    subj_id=$(echo "$line" | awk -F' ' '{ print $1 }')
    
    # Create run script with substituted variables
    sed -e "s|SUBJECT|${subj_id}|g" \
        -e "s|UV_PROJECT|${uv_proj_path}|g" \
        -e "s|CURR_DIR|${run_folder}|g" \
        "${check_template}" > "${check_folder}/run${k}"
    
    k=$((k+1))
done

# Set permissions
chmod 775 -R "${check_folder}"

echo "Created ${k} run scripts in ${check_folder}"