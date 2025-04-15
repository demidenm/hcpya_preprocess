#!/bin/bash

# Set types, models, and task list
types=("hcp" "alt")
models=("firstlvl" "fixedeff")
tasks=("language" "motor" "WM" "relational" "gambling" "social" "emotion")

# Output CSV file
output_file="s3_task-glm_file-counts.csv"

# Write header to CSV
#echo "Type,Model,Subject,Task,Run,FileCount" > "$output_file"

for type in "${types[@]}"; do
  for model in "${models[@]}"; do
    for task in "${tasks[@]}"; do
      
      if [[ "$model" == "firstlvl" ]]; then
        for run in 1 2; do
          # List subject directories
 #         s3cmd ls s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/ | \
 #           grep '\/$' | awk -F'/' '{print $(NF-1)}' | while read -r subj; do
          for subj in sub-111716 ; do

              path="s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/${subj}/${subj}_ses-3T_task-${task}_run-${run}_"
              count=$(s3cmd ls ${path}* 2>/dev/null | wc -l)
              echo "$type,$model,$subj,$task,$run,$count" >> "$output_file"
          done
        done

      elif [[ "$model" == "fixedeff" ]]; then
        # No runs for fixedeff
        #s3cmd ls s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/ | \
        #  grep '\/$' | awk -F'/' '{print $(NF-1)}' | while read -r subj; do
        for subj in sub-117021 sub-212318 sub-117122 sub-137128 sub-207426 sub-210415 sub-517239 sub-146331 sub-143224 sub-111716 sub-379657 sub-231928 sub-108323 ; do
            path="s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/${subj}/${subj}_ses-3T_task-${task}_"
            count=$(s3cmd ls ${path}* 2>/dev/null | wc -l)
            echo "$type,$model,$subj,$task,N/A,$count" >> "$output_file"
        done
      fi

    done
  done
done

