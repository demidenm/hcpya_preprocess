#!/bin/bash -l
#SBATCH -J hcp_glms
#SBATCH --array=0-399
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=8GB
#SBATCH --tmp=60gb
#SBATCH -t 01:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#amdsmall
#SBATCH -o logs/%x_%A_%a.out
#SBATCH -e logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

cd glmruns.3T

module load singularity
file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
