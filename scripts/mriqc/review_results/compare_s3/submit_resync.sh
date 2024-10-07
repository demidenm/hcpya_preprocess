#!/bin/bash -l
#SBATCH -J resync
#SBATCH --array=0,1 # jobs
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=4G
#SBATCH -t 4:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,amdsmall
#SBATCH -o resync_logs/%x_%A_%a.out
#SBATCH -e resync_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird #feczk001 


ID=${SLURM_ARRAY_TASK_ID}

bash ./rerun_jobs/resync${ID}

