#!/bin/bash
run_folder=$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
config_file="${run_folder}/config.json"
uv_proj_path=$(jq -r '.uv_proj.proj_dir' "$config_file")

echo
echo -e "Starting completion report using uv project path \n \t ${uv_proj_path}"
uv --project "${uv_proj_path}" run python prepost-proc_report.py
echo 
