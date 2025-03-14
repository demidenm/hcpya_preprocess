#!/bin/bash -l
#SBATCH -J xcpd_check
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32GB
#SBATCH --tmp=50gb
#SBATCH -t 00:30:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall
#SBATCH -o xcp_check_logs/%x_%A_%a.out
#SBATCH -e xcp_check_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

#source /home/faird/mdemiden/miniconda3/etc/profile.d/conda.sh
#conda activate fmri_env
# Using uv project path instead, see make_runs.sh

cd run_files.3T

file=run${SLURM_ARRAY_TASK_ID}
bash ${file}
