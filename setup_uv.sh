#!/bin/bash
 
# Check if uv is installed
if ! command -v uv &> /dev/null; then
	echo "uv not found. Installing..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
else
	echo "uv is already installed."
fi

# check if git is install, at least version 2.30.0
version_ge() { 
    [ "$(printf '%s\n' "$1" "$2" | sort -V | tail -n1)" == "$1" ]
}

# Check and install Git (version >= 2.30.0)
required_git_version="2.30.0"
if command -v git &> /dev/null; then
    current_git_version=$(git --version | awk '{print $3}')
    if version_ge "$current_git_version" "$required_git_version"; then
        echo "Git is up to date (version $current_git_version)."
    else
        echo "Updating Git to version $required_git_version..."
        conda install -y -c conda-forge git
    fi
else
    echo "Git is not installed. Installing..."
    conda install -y -c conda-forge git
fi


# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq not found. Installing..."
    if command -v conda &> /dev/null; then
        conda install -y -c conda-forge jq
    else
        echo "No supported package manager found for installing jq."
        exit 1
    fi
else
    echo "jq is already installed."
fi


# Proceed with setting up the environment based on pyproject.toml
source $HOME/.local/bin/env
uv sync

proj_dir=`pwd`
config_path="${proj_dir}/scripts/config.json"

if command -v jq &> /dev/null; then
    #  jq to add project dir to config for uv
    jq --arg dir "$proj_dir" '.uv_proj.proj_dir = $dir' ${config_path} > ${config_path}.tmp
    mv ${config_path}.tmp ${config_path}
    echo "Updated uv project dir in ./scripts/config.json"
else
    echo "jq is not installed, cannot updated .json"
fi
echo
echo
echo "uv is setup"
echo -e "\t to run scripts, point to uv project path ${proj_dir}"
echo -e "\t Example: "
echo -e "\t\t uv --project ${proj_dir} run python script_name.py "
echo
