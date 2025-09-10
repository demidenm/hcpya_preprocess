#!/bin/bash

# Set types, models, and task list
types=("hcp" "alt")
models=("firstlvl" "fixedeff")
tasks=("language" "motor" "WM" "relational" "gambling" "social" "emotion")

# Configuration
MAX_JOBS=${MAX_JOBS:-2}  # Number of parallel jobs
output_file="s3_task-glm_file-counts.csv"
temp_dir=$(mktemp -d)

# Function to process a single combination
process_combination() {
    local type=$1
    local model=$2
    local task=$3
    local run=$4
    local job_id=$5
    local temp_file="$temp_dir/result_${job_id}.csv"
    
    echo "Starting job $job_id: $type/$model/$task${run:+/run-$run} (PID: $$)"
    
    # Get subjects
    subjects=$(s3cmd ls s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/ | \
        grep '\/$' | awk -F'/' '{print $(NF-1)}')
    
    subject_count=$(echo "$subjects" | wc -l)
    echo "Job $job_id: Found $subject_count subjects"
    
    # Process subjects
    echo "$subjects" | while read -r subj; do
        if [[ -n "$subj" ]]; then
            if [[ -n "$run" ]]; then
                path="s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/${subj}/${subj}_ses-3T_task-${task}_run-${run}_"
                run_field="$run"
            else
                path="s3://hcp-youth/derivatives/task_glms/ses-3T/${type}/${model}/${subj}/${subj}_ses-3T_task-${task}_"
                run_field="N/A"
            fi
            
            count=$(s3cmd ls ${path}* 2>/dev/null | wc -l)
            echo "$type,$model,$subj,$task,$run_field,$count" >> "$temp_file"
        fi
    done
    
    echo "Job $job_id completed: $type/$model/$task${run:+/run-$run}"
}

# Create job array
declare -a jobs
job_count=0

for type in "${types[@]}"; do
    for model in "${models[@]}"; do
        for task in "${tasks[@]}"; do
            if [[ "$model" == "firstlvl" ]]; then
                for run in 1 2; do
                    jobs[job_count]="$type $model $task $run $job_count"
                    job_count=$((job_count + 1))
                done
            else
                jobs[job_count]="$type $model $task \"\" $job_count"
                job_count=$((job_count + 1))
            fi
        done
    done
done

echo "Total jobs: $job_count"
echo "Max parallel jobs: $MAX_JOBS"
echo "Starting processing at $(date)"
echo ""

# Process jobs with controlled parallelism
active_jobs=0
completed_jobs=0

for job in "${jobs[@]}"; do
    # Wait if we've hit the max job limit
    while [[ $active_jobs -ge $MAX_JOBS ]]; do
        wait -n  # Wait for any background job to complete
        active_jobs=$((active_jobs - 1))
        completed_jobs=$((completed_jobs + 1))
        echo "Progress: $completed_jobs/$job_count jobs completed"
    done
    
    # Start new job in background
    process_combination $job &
    active_jobs=$((active_jobs + 1))
done

# Wait for all remaining jobs
echo "Waiting for remaining jobs to complete..."
wait
completed_jobs=$job_count
echo "Progress: $completed_jobs/$job_count jobs completed"

echo ""
echo "Combining results..."

# Combine all temporary files in order
for ((i=0; i<job_count; i++)); do
    temp_file="$temp_dir/result_${i}.csv"
    if [[ -f "$temp_file" ]]; then
        cat "$temp_file" >> "$output_file"
    fi
done

# Cleanup
rm -rf "$temp_dir"

echo "Processing completed at $(date)"
echo "Results saved to: $output_file"
echo "Total lines in output: $(wc -l < "$output_file")"
