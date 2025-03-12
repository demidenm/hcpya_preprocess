import os
import pandas as pd
from pathlib import Path
import argparse
from preproc_util import (
    emotion_eprime_preproc,
    wm_eprime_preproc,
    language_eprime_preproc,
    relation_eprime_preproc,
    social_eprime_preproc,
    gamble_eprime_preproc,
    motor_eprime_preproc
)

# Function to process each subject
def process_subject(sub_file, task_name, dir_label, run_num, output_name):
    # assuming position of sub ID from HCP path -7. Seventh index from file name.
    subject = sub_file.parts[-7] 
    print(f"Starting subject sub-{subject}")
    
    # Read the input file
    events_file = pd.read_csv(sub_file, sep='\t')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_name, exist_ok=True)
    
    # Preprocess data based on task
    if task_name == 'EMOTION':
        converted_df = emotion_eprime_preproc(events_file)
    elif task_name == 'GAMBLING':
        converted_df = gamble_eprime_preproc(events_file)
    elif task_name == 'LANGUAGE':
        converted_df = language_eprime_preproc(events_file)
    elif task_name == 'MOTOR':
        converted_df = motor_eprime_preproc(events_file)
    elif task_name == 'RELATIONAL':
        converted_df = relation_eprime_preproc(events_file)
    elif task_name == 'SOCIAL':
        converted_df = social_eprime_preproc(events_file)
    elif task_name == 'WM':
        converted_df = wm_eprime_preproc(events_file)
    
    # Export the processed dataframe
    file_name = f"{output_name}/sub-{subject}_{session}_task-{task_name.lower()}_dir-{dir_label}_{run_num}_events.tsv"
    converted_df.to_csv(file_name, sep="\t", index=False)
    print(f"Processed file saved: {file_name}")

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process HCP E-Prime files')
parser.add_argument('--input', required=True, help='Path to HCP E-Prime folder')
parser.add_argument('--output', required=True, help='Path to output directory')
args = parser.parse_args()

# Configuration
hcp_eprime_folder = args.input
output_dir = args.output
session = "ses-3T"
task_names = ['EMOTION', 'MOTOR', 'RELATIONAL', 'SOCIAL', 'WM', 'GAMBLING', 'LANGUAGE']
runs = {
    "LR": "run2",
    "RL": "run1"
}


# Main processing loop
for task_name in task_names:
    print(f"Processing task: {task_name}")
    for dir_label, run_num in runs.items():
        files = sorted(Path(hcp_eprime_folder).rglob(f"*_3T_{task_name}_{run_num}_TAB.txt"))
        print(f"   Found {len(files)} subject files")
        for sub_file in files:
            # assuming position of sub ID from HCP path -7. Seventh index from file name.
            output_name = f"{output_dir}/sub-{sub_file.parts[-7]}/{session}/func"
            process_subject(sub_file, task_name, dir_label, run_num, output_name)

print("Processing completed")
print(f'\033[91m\tNote, subject ID was assumed to be the position of sub ID from HCP path -7. Check folder/file names\033[0m')